function imgFused = fuseLayersByVector(folder, prefix, selVec)
% fuseLayersByVector  Fusiona capas seleccionadas según un vector binario
%   folder  – Carpeta con imágenes
%   prefix  – Prefijo de las imágenes (antes de _N1_mask.bmp)
%   selVec  – Vector binario de 1×7 indicando qué capas usar

    idx = find(selVec);
    if isempty(idx)
        error('Vector vacío: no se seleccionó ninguna capa.');
    end

    imgFused = [];
    count    = 0;

    for k = idx
        fname = fullfile(folder, sprintf('%s_N%d_mask.bmp', prefix, k));
        if ~isfile(fname)
            warning('No existe %s — se omite capa %d', fname, k);
            continue;
        end
        img = im2double(imread(fname));
        if isempty(imgFused)
            imgFused = zeros(size(img));
        end
        imgFused = imgFused + img;
        count = count + 1;
    end

    if count == 0
        error('No se pudo leer ninguna capa seleccionada.');
    end

    imgFused = imgFused / count;
end
