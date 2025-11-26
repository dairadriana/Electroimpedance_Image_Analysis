function tf = prioridadNaranjaClaro(pixelRGB)
    r = pixelRGB(1);
    g = pixelRGB(2);
    b = pixelRGB(3);
    tf = (r > 0.7) && (g > 0.5) && (g < 0.7) && (b < 0.4);
end