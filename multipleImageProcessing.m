folder = 'C:\Users\tokyo\Desktop\Programming\Electroimpedance_Image_Analysis\Images\Prueba';

% Obtener archivos
archivos = dir(fullfile(folder, '*.bmp'));
prefijo = 'C0683d';
orden = strcat(prefijo, '_N', string(1:7), '_mask.bmp');
archivosOrdenados = archivos([]);

for i = 1:length(orden)
    idx = find(strcmpi({archivos.name}, orden(i)), 1);
    if ~isempty(idx)
        archivosOrdenados(end+1) = archivos(idx); %#ok<AGROW>
    end
end

fusionColor = [];
ocupadoMask = [];
imgFinal = [];

% Precargar fondo (N7)
for i = 1:length(archivosOrdenados)
    if endsWith(archivosOrdenados(i).name, '_N7_mask.bmp')
        imgFinal = im2double(imread(fullfile(folder, archivosOrdenados(i).name)));
        break;
    end
end

if isempty(imgFinal)
    error('Imagen base N7 no encontrada.');
end

% Inicializar overlay para etiquetas
labelOverlay = imgFinal;
textInfo = [];

for k = 1:length(archivosOrdenados)
    nombre = archivosOrdenados(k).name;
    imgPath = fullfile(folder, nombre);
    img = im2double(imread(imgPath));

    mask = redDetection(img);

    if isempty(fusionColor)
        fusionColor = zeros(size(img));
        ocupadoMask = false(size(mask));
    end

    nuevosPixeles = mask & ~ocupadoMask;

    % DIFUMINAR INTERIOR
    se = strel('disk', 3);
    erosion = imerode(nuevosPixeles, se);
    bordeInterno = nuevosPixeles & ~erosion;

    alphaMask = double(nuevosPixeles);
    alphaMask(bordeInterno) = 0.5;
    alphaSmooth = imgaussfilt(alphaMask, 2);
    alphaSmooth = min(max(alphaSmooth, 0), 1);

    % Mezclar
    for c = 1:3
        origen = img(:,:,c);
        fondo = imgFinal(:,:,c);
        fusionVals = origen .* alphaSmooth + fondo .* (1 - alphaSmooth);
        canal = fusionColor(:,:,c);
        canal(nuevosPixeles) = fusionVals(nuevosPixeles);
        fusionColor(:,:,c) = canal;
    end

    ocupadoMask = ocupadoMask | nuevosPixeles;

    % Extraer regiones y añadir etiquetas
    CC = bwconncomp(nuevosPixeles);
    stats = regionprops(CC, 'Centroid');
    for s = 1:length(stats)
        centroid = stats(s).Centroid;
        textInfo(end+1).Position = centroid; %#ok<AGROW>
        textInfo(end).Label = extractBetween(nombre, '_N', '_mask.bmp');
    end

    fprintf('Capas %s: %d regiones segmentadas\n', nombre, CC.NumObjects);
end

% Fusión final
finalMask = any(fusionColor > 0, 3);
imgCombinada = imgFinal;
for c = 1:3
    canalBase = imgFinal(:,:,c);
    canalFus  = fusionColor(:,:,c);
    canalBase(finalMask) = canalFus(finalMask);
    imgCombinada(:,:,c) = canalBase;
end

% Mostrar
figure;
imshow(imgCombinada);
title('Fusión con etiquetas de capa');

hold on;
for i = 1:length(textInfo)
    pos = textInfo(i).Position;
    label = textInfo(i).Label;
    text(pos(1), pos(2), sprintf('N%s', label{1}), ...
        'Color', 'yellow', 'FontSize', 10, 'FontWeight', 'bold');
end
hold off;
