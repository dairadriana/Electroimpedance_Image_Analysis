function [bestVec, bestScore, resultsTable] = searchBestLayerFusion_full(folder, prefix)
% searchBestLayerFusion_full  
% Evalúa exhaustivamente las 127 combinaciones de capas (excepto vector cero)
% Ahora usando computeFitness_Var3 = entropía + contraste – ruido – penalización no lineal.

    % ---- Configuración general ----
    N = 7;
    combos = dec2bin(1:(2^N-1)) - '0';
    combos = combos(combos(:,1)==1, :);  % Filtrar solo combinaciones donde capa 1 está activa

    numComb = size(combos,1);

    bestScore = -Inf;
    bestVec   = [];
    Results   = cell(numComb,4);   % SelVec, NumLayers, Score, Penalización

    fprintf('Evaluando %d combinaciones posibles...\n', numComb);

    % ---- Evaluación exhaustiva ----
    for i = 1:numComb
        sel = combos(i,:);          % vector binario 1x7
        nLayers = sum(sel);
        selStr = mat2str(sel);

        try
            imgF = fuseSelectedLayers(sel);    % fusión por promedio
            score = computeFitness_Var3(imgF, sel);  % <-- VARIANTE 3
        catch ME
            warning('Error en combinación %s: %s', selStr, ME.message);
            score = NaN;
        end

        Results{i,1} = sel;
        Results{i,2} = nLayers;
        Results{i,3} = score;
        Results{i,4} = nLayers^1.5;  % penalización aplicada

        if ~isnan(score) && score > bestScore
            bestScore = score;
            bestVec   = sel;
        end
    end

    resultsTable = cell2table(Results, ...
        'VariableNames', {'SelVec','NumLayers','Score','Penalty'});

    fprintf('\nMejor vector: %s → Score = %.4f\n', mat2str(bestVec), bestScore);

    % ============================================================
    % SUBFUNCIÓN: fusión por promedio de capas seleccionadas
    % ============================================================
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

        imgFuse = imgFuse / count;   % promedio final
    end

    % ============================================================
    % SUBFUNCIÓN: FITNESS VARIANTE 3
    % ============================================================
    function score = computeFitness_Var3(imgFuse, selVec)
        if isempty(imgFuse)
            score = -Inf;
            return;
        end

        % Pesos definidos por ti
        w1 = 1.0;   % entropía
        w2 = 2.0;   % contraste
        w3 = 0.01;  % ruido
        w4 = 0.3;   % penalización por capas

        red = imgFuse(:,:,1);

        % --- Entropía ---
        red_norm = mat2gray(red);
        e = entropy(red_norm);

        % --- Contraste ---
        s = std(red(:));

        % --- Ruido disperso ---
        bw = red > 0.1;
        CC = bwconncomp(bw);
        props = regionprops(CC, 'Area');
        areas = [props.Area];
        ruido = sum(areas(areas < 5));

        % --- Penalización no lineal ---
        numCapas = sum(selVec);
        penalty = w4 * (numCapas ^ 1.2);

        % Puntuación final
        score = w1*e + w2*s - w3*ruido - penalty;
    end
end
