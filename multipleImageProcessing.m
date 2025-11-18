folder = '...\Images\Prueba';  % <-- Cambia esta ruta

archivos = dir(fullfile(folder, '*.bmp'));
fprintf('Se encontraron %d imágenes .bmp en el folder.\n', length(archivos));

for k = 1:length(archivos)
    nombreCompleto = fullfile(folder, archivos(k).name);
    fprintf('Procesando: %s\n', archivos(k).name);

    img = imread(nombreCompleto);
    redDetection(img); 
end
