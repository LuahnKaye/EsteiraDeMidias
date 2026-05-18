def validar_assinatura_imagem(dados_binarios: bytes) -> bool:
    """
    Valida a assinatura física (Magic Bytes) de um buffer binário para garantir
    que se trata de uma imagem legítima do tipo PNG ou JPEG.

    Evita que arquivos maliciosos contendo extensões modificadas (como malware.exe
    renomeado para foto.png) sejam processados pela esteira de mídias.

    Args:
        dados_binarios (bytes): O fluxo de bytes brutos do cabeçalho da imagem.

    Returns:
        bool: Verdadeiro se a imagem tiver cabeçalho físico legítimo de PNG ou JPEG.
    """
    if len(dados_binarios) < 4:
        return False

    # Assinatura física do PNG (89 50 4E 47)
    magic_png = b'\x89PNG'
    
    # Assinatura física do JPEG/JPG (FF D8 FF)
    magic_jpeg = b'\xff\xd8\xff'

    # Verifica os Magic Bytes do arquivo
    se_png = dados_binarios.startswith(magic_png)
    se_jpeg = dados_binarios.startswith(magic_jpeg)

    # Se corresponder a um dos cabeçalhos, a imagem é considerada válida
    se_valida = se_png or se_jpeg
    return se_valida
