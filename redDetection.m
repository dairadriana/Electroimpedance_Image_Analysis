function redAreas = redDetection(img)
    % img debe ser RGB (uint8 o double [0,1])
    if ~isfloat(img)
        imgD = im2double(img);
    else
        imgD = img;
    end

    % Convertir a espacio HSV
    hsv = rgb2hsv(imgD);
    h   = hsv(:,:,1);  % hue
    s   = hsv(:,:,2);  % saturation
    v   = hsv(:,:,3);  % value (luminance)

    % Rango de tonos cafés/rojizos: ajustar según tus imágenes
    hueMin = 0.00;   % podrías ajustarlo a ~0.0 o ~0.02
    hueMax = 0.13;   % ~0.10 representa tonos rojizo‑naranja (h=0 es rojo en HSV)
    
    satMin  = 0.2;   % exigir cierta saturación
    valMin  = 0.15;   % exigir cierto valor mínimo

    maskHue = (h >= hueMin & h <= hueMax);
    maskSat = (s >= satMin);
    maskVal = (v >= valMin);

    % También podrías exigir que el canal rojo sea mayor que otros
    redChannel   = imgD(:,:,1);
    greenChannel = imgD(:,:,2);
    blueChannel  = imgD(:,:,3);
    dominanceMask = (redChannel > greenChannel + 0.03) & (redChannel > blueChannel + 0.03);

    % Máscara combinada
    redAreas = maskHue & maskSat & maskVal & dominanceMask;

    % Filtrar fondo negro muy oscuro
    backgroundMask = (redChannel < 0.05 & blueChannel < 0.05 & greenChannel < 0.05);
    redAreas(backgroundMask) = false;

    % Opcional: eliminar regiones muy pequeñas
    minArea = 10;
    redAreas = bwareaopen(redAreas, minArea);

    % Devolver máscara lógica
end
