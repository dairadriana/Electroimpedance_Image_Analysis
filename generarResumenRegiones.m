function generarResumenRegiones(mask, nombre)
    CC = bwconncomp(mask);
    if CC.NumObjects > 0
        stats = regionprops(CC, 'Area', 'Perimeter');
        areas = [stats.Area];
        perims = [stats.Perimeter];
        circ = 4*pi*(areas./(perims.^2));
        [areasSorted, idxSort] = sort(areas, 'descend');
        circSorted = circ(idxSort);
        fprintf('Capa %s → %d regiones detectadas\n', nombre, CC.NumObjects);
        fprintf('  Áreas (px): %s\n', num2str(areasSorted));
        fprintf('  Circularidad: %s\n', num2str(circSorted,'%.2f '));
    end
end
