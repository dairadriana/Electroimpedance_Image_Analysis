function ThermalImageRedApp()
    % Crear figura UI
    fig = uifigure('Name', 'Segmentación en Canal Rojo (con contraste)', ...
                   'Position', [100 100 900 600]);

    % Cargar imagen
    img = imread('C0683d_N1_mask.bmp');  % Reemplaza si es necesario
    imgD = im2double(img);
    img8 = im2uint8(imgD);

    % Extraer canales
    redChannel  = imgD(:,:,1);
    blueChannel = imgD(:,:,3);

    % Ajustar contraste del canal rojo
    redChannelAdj = imadjust(redChannel);

    % Crear eje para mostrar imagen
    ax = uiaxes(fig, 'Position', [50 100 512 384]);
    title(ax, 'Segmentación en canal rojo ajustado');

    % Etiqueta del umbral
    lbl = uilabel(fig, ...
        'Position', [600 420 180 22], ...
        'Text', 'Umbral canal rojo: 0.95');

    % Slider de umbral
    sld = uislider(fig, ...
        'Position', [580 400 200 3], ...
        'Limits', [0.7 1], ...
        'Value', 0.95, ...
        'MajorTicks', 0:0.1:1);

    % Callback principal
    function updateImage(~, ~)
        threshold = sld.Value;
        lbl.Text = sprintf('Umbral canal rojo: %.2f', threshold);

        % -------------------
        % Crear máscara por umbral sobre canal rojo ajustado
        redAreas = redChannelAdj > threshold;

        % Eliminar fondo negro
        backgroundMask = (redChannel < 0.05) & (blueChannel < 0.05);
        redAreas(backgroundMask) = false;

        % Conexión de regiones y filtrado
        CC = bwconncomp(redAreas);
        stats = regionprops(CC, 'Area', 'BoundingBox', 'Centroid');
        minArea = 50;
        validIdx = find([stats.Area] > minArea);

        % Crear imagen de overlay
        overlayImg = labeloverlay(img8, redAreas, ...
                                  'Transparency', 0.5, ...
                                  'Colormap', [1 0 1]);  % magenta

        % Mostrar en el eje
        imshow(overlayImg, 'Parent', ax);
        hold(ax, 'on');

        % Dibujar bounding boxes y centroides
        for k = validIdx
            rectangle(ax, 'Position', stats(k).BoundingBox, ...
                      'EdgeColor', 'g', 'LineWidth', 1.5);
            plot(ax, stats(k).Centroid(1), stats(k).Centroid(2), ...
                 'bo', 'MarkerSize', 5, 'LineWidth', 1.5);
        end

        hold(ax, 'off');
    end

    % Ejecutar inicial
    updateImage();

    % Conectar callback
    sld.ValueChangedFcn = @updateImage;
end
