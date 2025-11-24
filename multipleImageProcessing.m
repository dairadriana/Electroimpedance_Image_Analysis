% Ruta de la carpeta
folder = '...\Images\Prueba';  % <-- Ajusta esta ruta
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
inalMask = any(fusionColor > 0, 3);

% Crear máscara difusa como alfa
alpha = double(finalMask);
alpha = imdilate(alpha, strel('disk', 2));    % Suaviza borde
alpha = imgaussfilt(alpha, 2);                % Aplica desenfoque gaussiano
alpha = min(max(alpha, 0), 1);                % Clipa entre [0,1]

% Mezcla fusionada con fondo de N7
imgCombinada = imgFinal;
for c = 1:3
    base = imgFinal(:,:,c);
    inserto = fusionColor(:,:,c);
    
    % Evitar bordes negros: solo mezcla donde hay alfa > 0
    imgCombinada(:,:,c) = inserto .* alpha + base .* (1 - alpha);
end

% Mostrar resultado
figure;
imshow(imgCombinada);
title('Zonas fusionadas con prioridad y bordes difuminados');
