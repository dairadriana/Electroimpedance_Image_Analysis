function imgFuse = fuseWeightedRedPriority(folder, prefix, selVec, weightFactor)
% fuseWeightedRedPriority  Fusion ponderada dando más peso a píxeles rojizos
%
%   folder — carpeta con archivos .bmp (capas N1..N7)
%   prefix — prefijo común (ej. 'C0683d')
%   selVec — vector binario de largo N con capas a usar
%   weightFactor — factor de peso adicional para píxeles rojizos (>= 1)
%
%   Devuelve imgFuse (double en [0,1], RGB)

    if nargin < 4
        weightFactor = 2.0;  % por defecto: los píxeles rojizos pesan 2×
    end
    
    idx = find(selVec);
    if isempty(idx)
        error('No se seleccionó ninguna capa.');
    end
    
    % Leer la primera imagen para tamaño
    fname0 = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, idx(1)));
    img0   = im2double(imread(fname0));
    [H, W, C] = size(img0);
    
    % Inicializar acumuladores
    accumRGB     = zeros(H, W, C);
    accumWeight  = zeros(H, W);  % pesos sumados por píxel (escala 2D)
    
    for k = idx
        fname = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, k));
        if ~isfile(fname)
            warning('No existe %s — se omite capa %d', fname, k);
            continue;
        end
        img = im2double(imread(fname));
        
        % Construir máscara de "rojo relevante" para toda la capa
        hsv = rgb2hsv(img);
        h   = hsv(:,:,1);
        s   = hsv(:,:,2);
        v   = hsv(:,:,3);
        
        % Definir máscara de "colores de interés" (ajustar rangos según tus datos)
        maskBrownish = (h >= 0.00 & h < 0.05) & (s > 0.4) & (v > 0.2 & v < 0.6);
        maskReddish  = ((h >= 0.95 | h < 0.05) & (s > 0.5) & (v > 0.3));
        maskOrange   = (h >= 0.05 & h < 0.10) & (s > 0.4) & (v > 0.4);
        
        maskColor = maskBrownish | maskReddish | maskOrange;
        
        % Peso por pixel: si es de color de interés → weightFactor; si no → 1
        w = ones(H, W);
        w(maskColor) = weightFactor;
        
        % Acumular ponderadamente
        for c = 1:C
            accumRGB(:,:,c) = accumRGB(:,:,c) + img(:,:,c) .* w;
        end
        accumWeight = accumWeight + w;
    end
    
    % Evitar división por cero
    zeroMask = (accumWeight == 0);
    accumWeight(zeroMask) = 1;
    
    % Promedio ponderado
    imgFuse = zeros(H, W, C);
    for c = 1:C
        imgFuse(:,:,c) = accumRGB(:,:,c) ./ accumWeight;
    end
end
