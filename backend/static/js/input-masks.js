/**
 * input-masks.js
 * Sistema centralizado de máscaras e formatações de entrada
 */

class InputMask {
  /**
   * Inicializa máscaras em elementos do DOM
   * @param {string} selector - Seletor CSS ou tipo de campo
   * @param {string} maskType - Tipo de máscara
   */
  static apply(selector, maskType) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => {
      el.addEventListener('input', (e) => {
        e.target.value = this._applyMask(e.target.value, maskType);
      });
      // Limpar quando receber blur
      el.addEventListener('blur', (e) => {
        const cleaned = this._cleanValue(e.target.value, maskType);
        e.target.dataset.value = cleaned; // Armazenar valor limpo
      });
    });
  }

  /**
   * Aplicar máscara específica
   */
  static _applyMask(value, maskType) {
    const cleaned = value.replace(/\D/g, '');

    switch (maskType) {
      case 'cpf':
        return this._maskCPF(cleaned);
      case 'cnpj':
        return this._maskCNPJ(cleaned);
      case 'cpf_cnpj':
        return cleaned.length <= 11 ? this._maskCPF(cleaned) : this._maskCNPJ(cleaned);
      case 'phone':
        return this._maskPhone(cleaned);
      case 'cep':
        return this._maskCEP(cleaned);
      case 'plate':
        return this._maskPlate(value);
      case 'currency':
        return this._maskCurrency(value);
      case 'percentage':
        return this._maskPercentage(value);
      default:
        return value;
    }
  }

  /**
   * Limpar valor para enviar ao backend
   */
  static _cleanValue(value, maskType) {
    switch (maskType) {
      case 'currency':
        // "R$ 1.234,56" → "1234.56"
        return value.replace(/[^\d,]/g, '').replace(',', '.');
      case 'cep':
      case 'phone':
      case 'cpf':
      case 'cnpj':
      case 'cpf_cnpj':
        return value.replace(/\D/g, '');
      case 'plate':
        return value.replace(/[^A-Z0-9]/g, '').toUpperCase();
      default:
        return value.trim();
    }
  }

  // ==================== MÁSCARAS ESPECÍFICAS ====================

  static _maskCPF(value) {
    // "12345678901" → "123.456.789-01"
    return value
      .slice(0, 11)
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d{2})$/, '$1-$2');
  }

  static _maskCNPJ(value) {
    // "12345678901234" → "12.345.678/0001-34"
    return value
      .slice(0, 14)
      .replace(/(\d{2})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1.$2')
      .replace(/(\d{3})(\d)/, '$1/$2')
      .replace(/(\d{4})(\d{2})$/, '$1-$2');
  }

  static _maskPhone(value) {
    // "11987654321" → "(11) 98765-4321"
    if (value.length <= 10) {
      return value
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{4})(\d)/, '$1-$2');
    } else {
      return value
        .slice(0, 11)
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{5})(\d)/, '$1-$2');
    }
  }

  static _maskCEP(value) {
    // "12345678" → "12345-678"
    return value
      .slice(0, 8)
      .replace(/(\d{5})(\d)/, '$1-$2');
  }

  static _maskPlate(value) {
    // Handle both Mercosul (LLL9A99) and old Brazilian (LLL-9994) formats
    const cleaned = value.replace(/[^A-Z0-9]/g, '').toUpperCase().slice(0, 7);
    
    if (cleaned.length <= 3) return cleaned;
    
    // Detect Mercosul format (4th character is a digit)
    if (cleaned.length >= 4 && /\d/.test(cleaned[3])) {
      // Mercosul: ABC1D23
      if (cleaned.length <= 4) return cleaned;
      if (cleaned.length <= 5) return cleaned.slice(0, 4) + cleaned[4];
      return cleaned.slice(0, 4) + cleaned[4] + cleaned.slice(5);
    } else {
      // Old Brazilian: ABC-1234
      return cleaned.slice(0, 3) + '-' + cleaned.slice(3);
    }
  }

  static _maskCurrency(value) {
    // Formata como moeda brasileira: "1234.56" → "R$ 1.234,56"
    let num = value.replace(/[^\d,]/g, '').replace(',', '.');
    num = parseFloat(num) || 0;
    return 'R$ ' + num.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
  }

  static _maskPercentage(value) {
    // "75.5" → "75.5 %"
    const num = value.replace(/[^\d.]/g, '');
    if (num > 100) return '100 %';
    return num + ' %';
  }

  /**
   * Formatar data para exibição
   */
  static formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  }

  /**
   * Formatar moeda para exibição
   */
  static formatCurrency(value) {
    if (value === null || value === undefined) return 'R$ 0,00';
    return parseFloat(value).toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  }
}

// Exportar globalmente
window.InputMask = InputMask;

/**
 * Inicializar máscaras após carregar DOM
 */
document.addEventListener('DOMContentLoaded', () => {
  // CPF/CNPJ
  InputMask.apply('input[data-mask="cpf"]', 'cpf');
  InputMask.apply('input[data-mask="cnpj"]', 'cnpj');
  InputMask.apply('input[data-mask="cpf_cnpj"]', 'cpf_cnpj');

  InputMask.apply('input[data-mask="phone"]', 'phone');

  InputMask.apply('input[data-mask="cep"]', 'cep');

  InputMask.apply('input[data-mask="plate"]', 'plate');

  InputMask.apply('input[data-mask="currency"]', 'currency');

  InputMask.apply('input[data-mask="percentage"]', 'percentage');
});