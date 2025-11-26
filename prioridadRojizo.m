function tf = prioridadRojizo(pixelRGB)
    r = pixelRGB(1);
    g = pixelRGB(2);
    b = pixelRGB(3);
    tf = (r > 0.6) && (g < 0.5) && (b < 0.5) && ((r‑g) > 0.1) && ((r‑b) > 0.1);
end