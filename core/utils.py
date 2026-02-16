import re

def validate_rut(rut_str: str) -> bool:
    """
    Valida un RUT chileno aplicando el algoritmo de Módulo 11.
    Formato esperado: XX.XXX.XXX-X o XXXXXXXX-X
    """
    if not rut_str:
        return False
        
    rut = rut_str.replace(".", "").replace("-", "").upper()
    if len(rut) < 2:
        return False
        
    body, check_digit = rut[:-1], rut[-1]
    
    # Validar que el cuerpo sea numérico
    if not body.isdigit():
        return False
        
    # Calcular dígito verificador
    try:
        reversed_digits = map(int, reversed(body))
        factors = [2, 3, 4, 5, 6, 7]
        s = sum(d * f for d, f in zip(reversed_digits, factors * 10))
        res = 11 - (s % 11)
        
        if res == 11:
            calculated_dv = '0'
        elif res == 10:
            calculated_dv = 'K'
        else:
            calculated_dv = str(res)
            
        return check_digit == calculated_dv
    except Exception:
        return False

def format_clp(amount) -> str:
    """Formatea un número a formato CLP: $1.500"""
    if amount is None:
        return "$0"
    try:
        # Convertir a entero (truncar decimales si existen, CLP no usa centavos)
        val = int(amount)
        return "${:,.0f}".format(val).replace(",", ".")
    except ValueError:
        return str(amount)

def calculate_iva(net_amount):
    """Calcula el IVA (19%) sobre un monto neto (NO incluido en el precio base si se usa neto)."""
    # Si el precio base YA incluye IVA (regla de negocio 1), esta funcion extraería el IVA.
    # Regla usuario: "Impuesto IVA (19%) incluido". 
    # Por tanto, si amount es $1.190, IVA es $190.
    if net_amount is None:
        return 0
    return int(net_amount * 0.19)

def extract_iva_from_gross(gross_amount):
    """Extrae el IVA de un monto bruto."""
    if gross_amount is None:
        return 0
    net = int(gross_amount / 1.19)
    return gross_amount - net
