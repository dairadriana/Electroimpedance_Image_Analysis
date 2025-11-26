function [fitness, img_combinada] = evaluate_individual_matlab(image_folder, prefix, chromosome)
    % Evaluar un individuo representado por un vector binario de 7 elementos usando MATLAB
    %
    % Entradas:
    % - image_folder: string, carpeta con las imágenes
    % - prefix: string, prefijo de archivos (ej: 'C0683d')
    % - chromosome: array 1x7 de 0/1
    %
    % Salidas:
    % - fitness: double, puntuación
    % - img_combinada: array RGB double [0,1]

    if length(chromosome) ~= 7
        error('El cromosoma debe tener exactamente 7 elementos');
    end

    % Si todo ceros, seleccionar uno aleatoriamente
    if sum(chromosome) == 0
        idx = randi(7);
        chromosome(idx) = 1;
    end

    % Cargar imagen base N7
    base_path = fullfile(image_folder, sprintf('%s_N7_mask.bmp', prefix));
    if ~exist(base_path, 'file')
        error('Imagen base N7 no encontrada: %s', base_path);
    end
    img_ref = im2double(imread(base_path));

    img_size = size(img_ref(:,:,1));
    fusion_color = zeros(img_size(1), img_size(2), 3);
    ocupado_mask = false(img_size);

    hay_capas = false;

    % Procesar capas seleccionadas (N1 a N7)
    for i = 1:7
        if chromosome(i) == 0
            continue;
        end

        hay_capas = true;
        filename = sprintf('%s_N%d_mask.bmp', prefix, i);
        filepath = fullfile(image_folder, filename);
        if ~exist(filepath, 'file')
            warning('Falta %s, se omite', filepath);
            continue;
        end

        current_img = im2double(imread(filepath));
        mask = red_detection(current_img);

        new_pixels = mask & ~ocupado_mask;

        % Aplicar fusión
        for c = 1:3
            ch = fusion_color(:,:,c);
            temp = current_img(:,:,c);
            ch(new_pixels) = temp(new_pixels);
            fusion_color(:,:,c) = ch;
        end

        ocupado_mask = ocupado_mask | new_pixels;
    end

    if ~hay_capas
        fitness = -1.0;
        img_combinada = img_ref;
        return;
    end

    % Combinar con fondo
    final_mask = any(fusion_color > 0, 3);
    img_combinada = img_ref;
    for c = 1:3
        ch = img_combinada(:,:,c);
        temp = fusion_color(:,:,c);
        ch(final_mask) = temp(final_mask);
        img_combinada(:,:,c) = ch;
    end

    % Calcular fitness
    red_channel = img_combinada(:,:,1);
    red_8bit = uint8(red_channel * 255);

    % Entropía
    [counts, ~] = histcounts(red_8bit(:), 0:256);
    total = sum(counts);
    if total == 0
        e = 0.0;
    else
        p = counts / total;
        p_nonzero = p(p > 0);
        e = -sum(p_nonzero .* log(p_nonzero));
    end

    % Desviación estándar
    s = std(red_channel(:));

    % Penalización por ruido
    noise_threshold = 0.1;
    min_area = 5;
    binary = red_channel > noise_threshold;
    CC = bwconncomp(binary);
    stats = regionprops(CC, 'Area');
    if ~isempty(stats)
        areas = [stats.Area];
        ruido = sum(areas(areas < min_area));
    else
        ruido = 0.0;
    end

    % Pesos
    w1 = 1.0;
    w2 = 2.0;
    w3 = 0.01;

    fitness = (w1 * e) + (w2 * s) - (w3 * ruido);
end

function mask = red_detection(img, threshold)
    % Detecta zonas rojas como en redDetection.m
    if nargin < 2
        threshold = 0.96;
    end

    red_channel = img(:,:,1);
    blue_channel = img(:,:,3);

    % Equalizar histograma en rojo
    red_uint8 = uint8(red_channel * 255);
    red_eq = histeq(red_uint8) / 255.0;

    red_areas = red_eq > threshold;

    % Eliminar fondo negro
    background_mask = (red_channel < 0.05) & (blue_channel < 0.05);
    red_areas(background_mask) = false;

    mask = red_areas;
end