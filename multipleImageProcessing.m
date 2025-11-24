% Ruta de la carpeta
folder = 'C:\Users\tokyo\Desktop\Programming\Electroimpedance_Image_Analysis\Images\Prueba';  % <-- Ajusta esta ruta

prefijo = 'C0683d';
archivos = dir(fullfile(folder, '*.bmp'));

% Orden esperado de los archivos
orden = strcat(prefijo, '_N', string(1:7), '_mask.bmp');
archivosOrdenados = archivos([]);  % Inicializar como struct vacío

% Ordenar archivos por prioridad
for i = 1:length(orden)
    idx = find(strcmpi({archivos.name}, orden(i)), 1);
    if ~isempty(idx)
        archivosOrdenados(end+1) = archivos(idx); %#ok<AGROW>
    end
end

fusionColor = [];
ocupadoMask = [];
imgFinal = [];

for k = 1:length(archivosOrdenados)
    nombre = archivosOrdenados(k).name;
    imgPath = fullfile(folder, nombre);
    img = im2double(imread(imgPath));

    % Establecer N7 como imagen base
    if endsWith(nombre, '_N7_mask.bmp')
        imgFinal = img;
    end

    % Obtener máscara lógica (zonas rojas)
    mask = redDetection(img);  % Debe retornar una máscara binaria

    % Inicializar buffers
    if isempty(fusionColor)
        fusionColor = zeros(size(img));
        ocupadoMask = false(size(mask));
    end

    nuevosPixeles = mask & ~ocupadoMask;

    for c = 1:3
        canal = fusionColor(:,:,c);
        origen = img(:,:,c);
        canal(nuevosPixeles) = origen(nuevosPixeles);
        fusionColor(:,:,c) = canal;
    end

    ocupadoMask = ocupadoMask | nuevosPixeles;
end

% ------------------------
% DIFUMINAR BORDES
finalMask = any(fusionColor > 0, 3);

alpha = double(finalMask);
alpha = imdilate(alpha, strel('disk', 2));      % Expande bordes
alpha = imgaussfilt(alpha, 2);                  % Suaviza bordes
alpha = min(max(alpha, 0), 1);                  % Clipa a [0, 1]

% Mezcla con fondo (imgFinal)
imgCombinada = imgFinal;
for c = 1:3
    base = imgFinal(:,:,c);
    inserto = fusionColor(:,:,c);
    imgCombinada(:,:,c) = alpha .* inserto + (1 - alpha) .* base;
end

% Mostrar resultado
figure;
imshow(imgCombinada);
title('Zonas fusionadas con prioridad y bordes difuminados');
