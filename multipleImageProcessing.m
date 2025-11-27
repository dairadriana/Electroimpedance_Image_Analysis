folder = 'C:\Users\tokyo\Desktop\Programming\Electroimpedance_Image_Analysis\Images\EIM_B4';
[archivosOrdenados, imgFinal] = obtenerArchivosOrdenados(folder, 'C0793d');


fusionColor   = [];
ocupadoMask   = [];
etiquetas     = struct('BoundingBox', {}, 'Centroid', {}, 'Layer', {}, 'Area', {});
maskCombined  = false(size(imgFinal,1), size(imgFinal,2));

% Procesar cada capa
for k = 1:length(archivosOrdenados)
    nombre   = archivosOrdenados(k).name;
    imgPath  = fullfile(folder, nombre);
    img      = im2double(imread(imgPath));
    layerNum = k;

    % Obtener máscara de detección de zonas de interés
    mask = redDetection(img);

    % Generar resumen si hay regiones detectadas
    generarResumenRegiones(mask, nombre);   % revisar posible typo: generarResumenRegiones

    % Inicializar fusión en la primera iteración
    if isempty(fusionColor)
        fusionColor = zeros(size(img));            % asegura MxNx3
        ocupadoMask = false(size(mask));           % MxN lógico
    end

    nuevosPixeles = mask & ~ocupadoMask;

    CC2   = bwconncomp(nuevosPixeles);
    stats2 = regionprops(CC2, 'Area', 'BoundingBox', 'Centroid', 'PixelIdxList');

    % Ordenar regiones por área descendente
    areas2   = [stats2.Area];
    [~, order2] = sort(areas2, 'descend');
    keepLabel = false(numel(stats2),1);
    minDist   = 30;  % distancia mínima para evitar etiquetas cercanas

    for ii = 1:numel(stats2)
        idxReg = order2(ii);
        cent   = stats2(idxReg).Centroid;
        tooClose = false;
        for jj = find(keepLabel)'
            cent2 = stats2(jj).Centroid;
            if norm(cent - cent2) < minDist
                tooClose = true;
                break;
            end
        end
        if ~tooClose
            keepLabel(idxReg) = true;
        end
    end

    for ii = find(keepLabel)'
        pixIdx     = stats2(ii).PixelIdxList;
        regionMask = false(size(mask));
        regionMask(pixIdx) = true;

        maskCombined = maskCombined | regionMask;

        % Preparar transición suave con capas previas
        seDil       = strel('disk',3);
        dilNew      = imdilate(regionMask, seDil);
        dilOld      = imdilate(ocupadoMask, seDil);
        contactZone = dilNew & dilOld;

        distanceMap     = bwdist(~regionMask);
        maxDist         = 5;
        transitionMask  = (distanceMap > 0 & distanceMap <= maxDist) & contactZone;
        w               = zeros(size(mask));
        w(distanceMap>0 & distanceMap<=maxDist) = distanceMap(distanceMap>0 & distanceMap<=maxDist)/maxDist;

        % Mezcla canal por canal
        for c = 1:3
            origen = img(:,:,c);
            fondo  = imgFinal(:,:,c);
            canal  = fusionColor(:,:,c);

            canal(regionMask & ~transitionMask) = origen(regionMask & ~transitionMask);
            idxTrans = transitionMask;
            canal(idxTrans) = w(idxTrans).*origen(idxTrans) + (1-w(idxTrans)).*fondo(idxTrans);

            fusionColor(:,:,c) = canal;
        end

        ocupadoMask = ocupadoMask | regionMask;

        etiquetas(end+1).BoundingBox = stats2(ii).BoundingBox;
        etiquetas(end).Centroid     = stats2(ii).Centroid;
        etiquetas(end).Layer        = layerNum; 
        etiquetas(end).Area         = stats2(ii).Area; 
    end
end

etiquetas = filtrarEtiquetasPorTamanio(etiquetas, maskCombined, 400);

% Combinar imagen final
finalMask    = any(fusionColor>0,3);
imgCombinada = imgFinal;
for c = 1:3
    base = imgFinal(:,:,c);
    fus  = fusionColor(:,:,c);
    base(finalMask) = fus(finalMask);
    imgCombinada(:,:,c) = base;
end
redChannelAdj = imadjust(imgFinal(:,:,1));

mostrarResultados(imgFinal, etiquetas, redChannelAdj, maskCombined);
[bestVec, bestScore, tableAll] = searchBestLayerFusion_full(folder, prefix);
imgFusion = fuseLayersByVector(folder, prefix, bestVec);

% Mostrar
imshow(imgFusion);
title('Imagen fusionada por promedio (vector óptimo)');