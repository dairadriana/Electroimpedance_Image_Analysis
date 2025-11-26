function tf = prioridadCafeRojizo(pixelRGB)
    r = pixelRGB(1);
    g = pixelRGB(2);
    b = pixelRGB(3);
    % ejemplo: r alto, g y b más bajos, tono un poco "marrón"
    tf = (r > 0.6) && (g < 0.4) && (b < 0.4) && ((r‑g) > 0.2) && ((r‑b) > 0.2);
end