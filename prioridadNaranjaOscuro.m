function tf = prioridadNaranjaOscuro(pixelRGB)
    r = pixelRGB(1);
    g = pixelRGB(2);
    b = pixelRGB(3);
    % naranja‐oscuro: r y g relativamente altos, b bajo
    tf = (r > 0.6) && (g > 0.3) && (g < 0.6) && (b < 0.3);
end