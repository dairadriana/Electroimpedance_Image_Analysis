function redAreas = redDetection(img)
    % img debe ser una imagen RGB (tipo uint8 o double en [0,1])

    % Convertir a double si es necesario
    if ~isfloat(img)
        imgD = im2double(img);
    else
        imgD = img;
    end

    % Nos dimos cuenta de que se trabaja mejor sobre el canal azul
    redChannel   = imgD(:,:,1);
    blueChannel  = imgD(:,:,3);

    redChannelAdj = imadjust(redChannel);

    % ---------------------
    % Umbral en rojo
    threshold = 0.95;  % Ajustado por formato repetitivo en todas las imágenes 
    redAreas = redChannelAdj > threshold;

    % ------------------
    % Creamos una máscara que detecta el fondo
    backgroundMask = (redChannel < 0.05) & (blueChannel < 0.05);
    redAreas(backgroundMask) = false;

    % ----------------------
    % Mostrar imagen de zonas aisladas
    isolatedRedAreas = redChannelAdj .* redAreas;
    %figure;
    %imshow(isolatedRedAreas);
    %title('Zonas rojas aisladas (sin fondo)');

    % -------------------
    % Visualización en color (superposición)
    img8 = im2uint8(imgD); 
    %overlayColor = [1 0 1];  % Magenta (lo podemos cambiar)

    %overlayImg = labeloverlay(img8, redAreas, ...
    %    'Transparency', 0.5, ...
    %    'Colormap', overlayColor);

    %figure;
    %imshow(overlayImg);
    %title('Zonas umbralizadas resaltadas (sin pintar fondo)');
end
