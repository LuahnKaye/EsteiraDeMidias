import pytest
from src.dominio.validador_assinatura import validar_assinatura_imagem

def test_deve_retornar_verdadeiro_para_imagem_png_valida():
    """
    Testa se o validador reconhece corretamente os Magic Bytes de uma imagem PNG legítima.
    """
    bytes_png = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x00"
    resultado = validar_assinatura_imagem(bytes_png)
    assert resultado is True

def test_deve_retornar_verdadeiro_para_imagem_jpeg_valida():
    """
    Testa se o validador reconhece corretamente os Magic Bytes de uma imagem JPEG legítima.
    """
    bytes_jpeg = b"\xff\xd8\xff\xe0" + b"\x00\x00\x00\x00"
    resultado = validar_assinatura_imagem(bytes_jpeg)
    assert resultado is True

def test_deve_retornar_falso_para_arquivo_malicioso_disfarcado():
    """
    Testa se o validador bloqueia um script de shell malicioso que tentou se passar por imagem.
    """
    bytes_maliciosos = b"#!/bin/bash\necho 'hack_realizado'"
    resultado = validar_assinatura_imagem(bytes_maliciosos)
    assert resultado is False

def test_deve_retornar_falso_para_arquivo_vazio():
    """
    Testa o comportamento de seguranca caso um upload vazio seja enviado.
    """
    bytes_vazios = b""
    resultado = validar_assinatura_imagem(bytes_vazios)
    assert resultado is False
