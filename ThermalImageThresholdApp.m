function ThermalFusionApp()
    % Crear figura
    fig = uifigure('Name', 'Fusión Térmica con Bordes Suaves', ...
                   'Position', [100 100 1000 600]);

    % Cargar imágenes (ajusta rutas si es necesario)
    imgBase = im2double(imread('C0683d_N7_mask.bmp'));  % imagen de fondo
    imgN1 = im2double(imread('C0683d_N1_mask.bmp'));    % capa principal a controlar

    img8 = im2uint8(imgN1);
    redChannel = imgN1(:,:,1);
    blueChannel = imgN1(:,:,3);
    redChannelAdj = imadjust(redChannel);

    % Eje para visualización
    ax = uiaxes(fig, 'Position', [50 100 512 384]);
    title(ax, 'Vista previa de segmentación');

    % Etiqueta del umbral
    lbl = uilabel(fig, ...
        'Position', [600 420 200 22], ...
        'Text', 'Umbral canal rojo: 0.95');

    % Slider
    sld = uislider(fig, ...
        'Position', [580 400 200 3], ...
        'Limits', [0.7 1], ...
        'Value', 0.95, ...
        'MajorTicks', 0.7:0.05:1);

    % Botón para aplicar fusión
    btn = uibutton(fig, 'Text', 'Aplicar Fusión', ...
        'Position', [600 350 150 30], ...
        'ButtonPushedFcn', @(~,~) aplicarFusion());

    % Callback para actualizar la imagen
    function updateImage(~, ~)
        threshold = sld.Value;
        lbl.Text = sprintf('Umbral canal rojo: %.2f', threshold);
        mask = (redChannelAdj > threshold);
        backgroundMask = (redChannel < 0.05) & (blueChannel < 0.05);
        mask(backgroundMask) = false;

        overlay = labeloverlay(img8, mask, ...
            'Transparency', 0.5, 'Colormap', [1 0 1]);

        imshow(overlay, 'Parent', ax);
    end

    % Fusión con bordes difuminados
    function aplicarFusion()
        threshold = sld.Value;
        mask = (redChannelAdj > threshold);
        backgroundMask = (redChannel < 0.05) & (blueChannel < 0.05);
        mask(backgroundMask) = false;

        % Crear borde suave interno
        se = strel('disk', 3);
        erosion = imerode(mask, se);
        borde = mask & ~erosion;
        alphaMask = double(mask);
        alphaMask(borde) = 0.5;
        alphaSmooth = imgaussfilt(alphaMask, 1.5);
        alphaSmooth = min(max(alphaSmooth, 0), 1);

        % Fusión canal por canal
        imgFusionada = imgBase;
        for c = 1:3
            capa = imgN1(:,:,c);
            base = imgBase(:,:,c);
            imgFusionada(:,:,c) = capa .* alphaSmooth + base .* (1 - alphaSmooth);
        end

        figure;
        imshow(imgFusionada);
        title('Imagen fusionada con transición suave');
    end

    % Inicial
    updateImage();
    sld.ValueChangedFcn = @updateImage;
end
