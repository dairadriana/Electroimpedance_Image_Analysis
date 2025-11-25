function redAreas = redDetection(img)
    % Convertir a double si es necesario
    if ~isfloat(img)
        imgD = im2double(img);
    else
        imgD = img;
    end

    redChannel   = imgD(:,:,1);
    greenChannel = imgD(:,:,2);
    blueChannel  = imgD(:,:,3);

    redChannelAdj = imadjust(redChannel);

    % Umbral de intensidad para rojos brillantes
    threshold = 0.92;
    redMask = redChannelAdj > threshold;

    % Dominancia: permitir algunos naranjas
    dominanceMargin = 0.05;
    colorDominanceMask = (redChannel > greenChannel + dominanceMargin) & ...
                         (redChannel > blueChannel + 0.1);  % Más estricto con azul

    % Eliminar fondo negro
    backgroundMask = (redChannel < 0.05) & (blueChannel < 0.05);

    % Máscara final
    redAreas = redMask & colorDominanceMask;
    redAreas(backgroundMask) = false;
end
