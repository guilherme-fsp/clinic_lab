from guardrails.pii import detect_pii, mask_pii


def test_detect_pii_finds_expected_entities():

    text = """
Paciente: João da Silva
CPF: 123.456.789-00
Telefone: (21) 99999-9999
Email: joao@email.com
Data de Nascimento: 10/05/1990
"""

    entities = detect_pii(text)

    entity_types = {
        entity.entity_type
        for entity in entities
    }

    assert "PERSON" in entity_types
    assert "CPF" in entity_types
    assert "PHONE" in entity_types
    assert "EMAIL" in entity_types
    assert "DATE_OF_BIRTH" in entity_types


def test_mask_pii_removes_sensitive_values():

    text = """
Paciente: João da Silva
CPF: 123.456.789-00
Telefone: (21) 99999-9999
Email: joao@email.com
Data de Nascimento: 10/05/1990

Exames:
Hemograma Completo
Glicemia
"""

    result = mask_pii(text)

    assert "João da Silva" not in result.sanitized_text
    assert "123.456.789-00" not in result.sanitized_text
    assert "(21) 99999-9999" not in result.sanitized_text
    assert "joao@email.com" not in result.sanitized_text
    assert "10/05/1990" not in result.sanitized_text

    assert "Hemograma Completo" in result.sanitized_text
    assert "Glicemia" in result.sanitized_text


def test_mask_pii_adds_expected_placeholders():

    text = """
Paciente: João da Silva
CPF: 123.456.789-00
"""

    result = mask_pii(text)

    assert "[PERSON_" in result.sanitized_text
    assert "[CPF_" in result.sanitized_text


def test_text_without_pii_is_preserved():

    text = """
Exames:
Hemograma Completo
Glicemia
Colesterol Total
"""

    result = mask_pii(text)

    assert result.sanitized_text == text
    assert result.detected_entities == []