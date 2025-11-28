function imgFuse = fuseWeightedSmooth(folder, prefix, selVec, weightBrown, weightRed, weightOrange, sigmaSmooth)
% fuseWeightedSmooth  Fusion ponderada dando peso mayor a cafés/rojos/naranjas, con transición suave
%
% folder, prefix, selVec  — igual que antes
% weightBrown  — peso para píxeles "café/rojizo oscuro"
% weightRed    — peso para píxeles "rojo"
% weightOrange — peso para píxeles "naranja"
% sigmaSmooth — sigma del filtro Gaussiano para suavizar la máscara de peso
%
% imgFuse — imagen resultante fusionada (double [0,1], RGB)

    if nargin < 4, weightBrown  = 2.5; end
    if nargin < 5, weightRed    = 2.0; end
    if nargin < 6, weightOrange = 1.5; end
    if nargin < 7, sigmaSmooth  = 3; end

    idx = find(selVec);
    if isempty(idx)
        error('No se seleccionó ninguna capa.');
    end

    % Leer primera imagen para dimensiones
    fname0 = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, idx(1)));
    img0   = im2double(imread(fname0));
    [H, W, C] = size(img0);

    accumWeighted = zeros(H, W, C);
    accumWeight   = zeros(H, W);

    for k = idx
        fname = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, k));
        if ~isfile(fname)
            warning('No existe %s — se omite capa %d', fname, k);
            continue;
        end
        img = im2double(imread(fname));

        % Convertir a HSV para clasificar color
        hsv = rgb2hsv(img);
        h = hsv(:,:,1);
        s = hsv(:,:,2);
        v = hsv(:,:,3);

        % Máscaras de interés
        maskBrownish = (h >= 0.00 & h < 0.05) & (s > 0.4) & (v > 0.2 & v < 0.6);
        maskRed      = ((h >= 0.95 | h < 0.05) & (s > 0.5) & (v > 0.3));
        maskOrange   = (h >= 0.05 & h < 0.10) & (s > 0.4) & (v > 0.4);

        w = ones(H, W);
        w(maskBrownish) = weightBrown;
        w(maskRed)      = max(w(maskRed), weightRed);
        w(maskOrange)   = max(w(maskOrange), weightOrange);

        % Acumular ponderadamente
        for c = 1:C
            accumWeighted(:,:,c) = accumWeighted(:,:,c) + img(:,:,c) .* w;
        end
        accumWeight = accumWeight + w;
    end

    % Imagen promedio base (fondo neutro)
    imgMean = meanStack(folder, prefix, selVec, H, W, C);

    % Construir máscara de peso global normalizada
    alpha = accumWeight;
    alpha = alpha - min(alpha(:));
    alpha = alpha / max(alpha(:));

    % Suavizar para evitar bordes duros
    alphaSmooth = imgaussfilt(alpha, sigmaSmooth);

    % Mezcla final: ponderado dominante + fondo neutro según alpha
    imgFuse = zeros(H, W, C);
    for c = 1:C
        imgFuse(:,:,c) = alphaSmooth .* (accumWeighted(:,:,c) ./ accumWeight) + ...
                         (1 - alphaSmooth) .* imgMean(:,:,c);
    end
end

function imgMean = meanStack(folder, prefix, selVec, H, W, C)
    idx = find(selVec);
    imgMean = zeros(H, W, C);
    count   = 0;
    for k = idx
        fname = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, k));
        if ~isfile(fname), continue; end
        img = im2double(imread(fname));
        imgMean = imgMean + img;
        count = count + 1;
    end
    imgMean = imgMean / count;
end
