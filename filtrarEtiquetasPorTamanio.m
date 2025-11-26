function etiquetasOut = filtrarEtiquetasPorTamanio(etiquetas, maskCombined, areaUmbral)
    N     = numel(etiquetas);
    show  = true(1,N);
    masks = cell(1,N);

    for i = 1:N
        bb = round(etiquetas(i).BoundingBox);
        mask_i = false(size(maskCombined));
        mask_i(bb(2):bb(2)+bb(4)-1, bb(1):bb(1)+bb(3)-1) = true;
        masks{i} = mask_i;
    end

    se = strel('disk',2);

    for i = 1:N
        if ~show(i)
            continue;
        end
        area_i = etiquetas(i).Area;
        dil_i  = imdilate(masks{i}, se);
        for j = 1:N
            if i==j || ~show(j)
                continue;
            end
            if any(dil_i(:) & masks{j}(:))
                area_j = etiquetas(j).Area;
                if area_i < areaUmbral && area_j > area_i
                    show(i) = false;
                elseif area_j < areaUmbral && area_i > area_j
                    show(j) = false;
                end
            end
        end
    end

    etiquetasOut = etiquetas(show);
end
