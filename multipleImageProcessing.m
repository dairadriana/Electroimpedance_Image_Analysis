% Ruta de la carpeta
folder = '/home/ashley/projects/Electroimpedance_Image_Analysis/Images/Prueba';  % <-- Ajusta esta ruta

% Obtener lista de archivos en la carpeta
archivos = dir(fullfile(folder, '*.bmp'));

% Prefijo y sufijos
prefijo = 'C0683d';
sufijosPermitidos = strcat('_N', string(1:7), '_mask');

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

for k = 1:length(archivosOrdenados)
    nombre = archivosOrdenados(k).name;
    imgPath = fullfile(folder, nombre);
    img = im2double(imread(imgPath));

    % Usar N7 como fondo final
    if endsWith(nombre, '_N7_mask.bmp')
        imgFinal = img;
    end

    mask = redDetection(img);  % devuelve máscara lógica

    % Inicializar imagen de salida y máscara de ocupación
    if isempty(fusionColor)
        fusionColor = zeros(size(img));
        ocupadoMask = false(size(mask));
    end

    % Calcular los píxeles que aún no han sido asignados
    nuevosPixeles = mask & ~ocupadoMask;

    % Insertar en la imagen final por prioridad
    for c = 1:3
        canal = fusionColor(:,:,c);
        origen = img(:,:,c);  % ← usar variable intermedia
        canal(nuevosPixeles) = origen(nuevosPixeles);
        fusionColor(:,:,c) = canal;
    end

    ocupadoMask = ocupadoMask | nuevosPixeles;
end

% Combinar sobre la imagen final (N7)
finalMask = any(fusionColor > 0, 3);
imgCombinada = imgFinal;
for c = 1:3
    canal = imgFinal(:,:,c);
    origen = fusionColor(:,:,c);  % variable intermedia
    canal(finalMask) = origen(finalMask);
    imgCombinada(:,:,c) = canal;
end

% Mostrar resultado
figure;
imshow(imgCombinada);
title('Zonas fusionadas (prioridad N1 → N7, color original)');