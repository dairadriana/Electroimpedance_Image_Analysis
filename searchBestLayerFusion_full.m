function [bestVec, bestScore, resultsTable] = searchBestLayerFusion_full(folder, prefix)
% searchBestLayerFusion_full  Evalúa exhaustivamente combinaciones de capas
%   folder: carpeta con las imágenes .bmp (capas N1..N7)
%   prefix: prefijo común (antes de _N1_mask.bmp, etc.)
%
% Salidas:
%   bestVec      – vector binario 1×7 con la mejor combinación
%   bestScore    – fitness de la mejor combinación
%   resultsTable – tabla con todas las combinaciones y sus scores

    N = 7;
    combos = dec2bin(1:(2^N-1)) - '0';
    numComb = size(combos,1);

    bestScore = -Inf;
    bestVec   = [];
    Results   = cell(numComb,3);

    fprintf('Evaluando %d combinaciones posibles...\n', numComb);

    for i = 1:numComb
        sel = combos(i,:);
        selStr = mat2str(sel);
        try
            imgF = fuseSelectedLayers(sel);
            score = computeFitness(imgF);
        catch ME
            warning('Error en combinación %s: %s', selStr, ME.message);
            score = NaN;
        end

        Results{i,1} = sel;
        Results{i,2} = sum(sel);  % número de capas usadas
        Results{i,3} = score;

        if ~isnan(score) && score > bestScore
            bestScore = score;
            bestVec   = sel;
        end
    end

    resultsTable = cell2table(Results, 'VariableNames', {'SelVec','NumLayers','Score'});
    fprintf('\nMejor vector: %s → Score = %.4f\n', mat2str(bestVec), bestScore);

    % Subfunción: fusionar capas seleccionadas
    function imgFuse = fuseSelectedLayers(selVec)
        idx = find(selVec);
        if isempty(idx)
            error('Vector vacío: no se seleccionó ninguna capa.');
        end
        imgFuse = [];
        count  = 0;
        for k = idx
            fname = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, k));
            if ~isfile(fname)
                warning('No existe %s — se omite capa %d', fname, k);
                continue;
            end
            img = im2double(imread(fname));
            if isempty(imgFuse)
                imgFuse = zeros(size(img));
            end
            imgFuse = imgFuse + img;
            count = count + 1;
        end
        if count == 0
            error('No se pudo leer ninguna capa seleccionada.');
        end
        imgFuse = imgFuse / count;
    end

    % Subfunción: calcular fitness
    function score = computeFitness(img)
        if isempty(img)
            score = -Inf;
            return;
        end
        red = img(:,:,1);

        % Entropía global
        red_norm = mat2gray(red);
        e = entropy(red_norm);

        % Contraste (desviación estándar)
        s = std(red(:));

        % Ruido disperso: regiones pequeñas
        noise_thresh = 0.1;
        min_area     = 5;
        bw = red > noise_thresh;
        CC = bwconncomp(bw);
        props = regionprops(CC, 'Area');
        areas = [props.Area];
        noise = sum(areas(areas < min_area));

        w1 = 1.0; w2 = 2.0; w3 = 0.01;
        score = w1*e + w2*s - w3*noise;
    end
end
