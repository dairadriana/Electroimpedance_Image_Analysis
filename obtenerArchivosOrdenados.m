function [archivosOrdenados, imgFinal] = obtenerArchivosOrdenados(folder, prefijo)
    archivos = dir(fullfile(folder, '*.bmp'));
    orden = strcat(prefijo, '_N', string(1:7), '_mask.bmp');
    archivosOrdenados = archivos([]);  

    for i = 1:length(orden)
        idx = find(strcmpi({archivos.name}, orden(i)), 1);
        if ~isempty(idx)
            archivosOrdenados(end+1) = archivos(idx); %#ok<AGROW>
        end
    end

    imgFinal = [];
    for i = 1:length(archivosOrdenados)
        if endsWith(archivosOrdenados(i).name, '_N1_mask.bmp')
            imgFinal = im2double(imread(fullfile(folder, archivosOrdenados(i).name)));
            break;
        end
    end

    if isempty(imgFinal)
        error('Imagen base N7 no encontrada.');
    end
end
