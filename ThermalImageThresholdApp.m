function ThermalImageThresholdApp()
    % Crear figura UI
    fig = uifigure('Name', 'Umbralización de Imagen Térmica', ...
                   'Position', [100 100 900 600]);

    % -------------------
    % Cargar imagen
    img = imread('C0683d_N1_mask.bmp');  % Cambia si es necesario
    imgD = im2double(img);

    % Canales
    redChannel  = imgD(:,:,1);
    blueChannel = imgD(:,:,3);

    % Convertir imagen a uint8 para overlay
    img8 = im2uint8(imgD);

    % -------------------
    % Eje para imagen
    ax = uiaxes(fig, 'Position', [50 100 512 384]);
    title(ax, 'Zonas umbralizadas sobre imagen original (sin fondo)');

    % -------------------
    % Etiqueta del slider
    lbl = uilabel(fig, ...
        'Position', [600 420 180 22], ...
        'Text', 'Umbral canal azul: 0.30');

    % Slider de umbral
    sld = uislider(fig, ...
        'Position', [580 400 200 3], ...
        'Limits', [0 1], ...
        'Value', 0.30, ...
        'MajorTicks', 0:0.1:1);

    % -------------------
    % CALLBACK PRINCIPAL
    function updateImage(~, ~)
        threshold = sld.Value;
        lbl.Text = sprintf('Umbral canal azul: %.2f', threshold);

        % -------------------
        % MÁSCARA BASE POR UMBRAL EN CANAL AZUL
        redAreas = (blueChannel < threshold);

        % -------------------
        % ELIMINAR FONDO NEGRO
        backgroundMask = (redChannel < 0.05) & (blueChannel < 0.05);
        redAreas(backgroundMask) = false;

        % -------------------
        % CREAR OVERLAY
        overlayImg = labeloverlay(img8, redAreas, ...
            'Transparency', 0.5, ...
            'Colormap', [1 0 1]);   % magenta

        % Mostrar
        imshow(overlayImg, 'Parent', ax);
    end

    % Correr una vez al inicio
    updateImage();

    % Conectar slider al callback
    sld.ValueChangedFcn = @updateImage;
end
