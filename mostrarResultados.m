function mostrarResultados(imgBase, etiquetas, canalInteres, maskCombined)
    % imgBase       – imagen térmica RGB M×N×3 (colores intactos)
    % etiquetas     – struct array con campos BoundingBox, Centroid, Layer, Area
    % canalInteres  – M×N matriz (por ejemplo canal rojo ajustado)
    % maskCombined  – M×N lógica de zonas detectadas

    colores = [ ...
        1.00 0.00 0.00;   % N1 rojo
        0.00 1.00 0.00;   % N2 verde
        0.00 0.00 1.00;   % N3 azul
        1.00 0.50 0.00;   % N4 naranja
        0.50 0.00 0.50;   % N5 púrpura
        0.00 0.75 0.75;   % N6 turquesa
        0.75 0.75 0.00    % N7 amarillo oliva
    ];

    % Figura 1: imagen base sin etiquetas
    figure;
    imshow(imgBase);
    title('Imagen térmica original (sin etiquetas)');

    % Figura 2: imagen base + overlay mapa de calor + etiquetas
    figure;
    imshow(imgBase);
    hold on;
    % Overlay de mapa de calor
    h = imagesc(canalInteres);
    colormap(h.Parent, jet);
    colorbar(h.Parent);
    set(h, 'AlphaData', 0.25);   % transparencia 25%
    % Dibujar etiquetas
    for i = 1:numel(etiquetas)
        bb   = etiquetas(i).BoundingBox;
        cent = etiquetas(i).Centroid;
        capa = etiquetas(i).Layer;
        color = colores(capa,:);
        rectangle('Position', bb, 'EdgeColor', color, 'LineWidth', 1.5);
        text(cent(1), cent(2), sprintf('N%d', capa), ...
             'Color', color, 'FontWeight','bold','FontSize',10);
    end
    hold off;
    title('Imagen térmica con overlay de calor y etiquetas');

    % Figura 3: máscara binaria con etiquetas
    figure;
    imshow(maskCombined);
    title('Máscara binaria de zonas detectadas');
    hold on;
    for i = 1:numel(etiquetas)
        cent = etiquetas(i).Centroid;
        capa = etiquetas(i).Layer;
        color = colores(capa,:);
        text(cent(1), cent(2), sprintf('N%d', capa), ...
             'Color', color, 'FontWeight','bold','FontSize',10);
    end
    hold off;
end
