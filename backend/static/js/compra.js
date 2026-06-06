/**
 * compra.js
 * * Utilitário focado em operações transacionais de checkout e pedidos.
 * Centraliza a comunicação com o ecossistema de vendas da API.
 */

/**
 * Envia o carrinho completo e dados de entrega para finalização atômica do checkout
 * @param {Object} checkoutData - Dados estruturados para o fechamento da compra
 * @param {Array} checkoutData.itens - Lista de objetos { id_produto, quantidade }
 * @param {number} checkoutData.id_veiculo - ID do veículo selecionado pelo cliente
 * @param {string} checkoutData.endereco - Endereço completo para entrega/faturamento
 * @param {number} checkoutData.frete - Valor calculado do frete
 * @returns {Promise<Object>} - Dados do pedido gerado, notas e status atual
 */
async function finalizarCheckout(checkoutData) {
    try {
        // Validação defensiva no front antes do disparo de rede
        if (!checkoutData.itens || checkoutData.itens.length === 0) {
            throw new Error("Não é possível finalizar um pedido com o carrinho vazio.");
        }
        if (!checkoutData.id_veiculo) {
            throw new Error("Por favor, selecione um veículo cadastrado para prosseguir.");
        }
        if (!checkoutData.endereco || checkoutData.endereco.trim() === "") {
            throw new Error("O endereço de entrega é obrigatório para o cálculo e envio.");
        }

        // Item 3: Chamada ao endpoint atômico unificado (Evita requisições fragmentadas)
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Envia os cookies de sessão e tokens de autenticação
            body: JSON.stringify({
                itens: checkoutData.itens.map(item => ({
                    id_produto: item.id_produto,
                    quantidade: item.quantidade
                })),
                id_veiculo: parseInt(checkoutData.id_veiculo, 10),
                endereco: checkoutData.endereco.trim(),
                frete: parseFloat(checkoutData.frete) || 0
            })
        });

        const data = await response.json();

        if (!response.ok) {
            // Trata erros de negócio capturados pelo backend (ex: Estoque Insuficiente - Item 5)
            throw new Error(data.detail || 'Falha ao processar o checkout.');
        }

        return data; // Retorna o payload estruturado: { pedido: {...}, itens: [...] }
    } catch (error) {
        console.error('Erro na operação de checkout:', error);
        throw error;
    }
}

/**
 * Solicita o cancelamento de um pedido pendente, devolvendo os itens ao estoque
 * @param {number} pedidoId - ID do pedido a ser cancelado
 * @returns {Promise<Object>} - Resultado da operação com status atualizado
 */
async function cancelarPedido(pedidoId) {
    try {
        // Item 12 e 13: Ocorre a reposição automática no banco caso o status seja 'pendente'
        const response = await fetch(`/api/pedidos/${pedidoId}/cancelar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Não foi possível cancelar o pedido.');
        }

        return data;
    } catch (error) {
        console.error(`Erro ao cancelar o pedido #${pedidoId}:`, error);
        throw error;
    }
}

// Exportação global limpa, focada no fluxo transacional do Ajuste 4
window.finalizarCheckout = finalizarCheckout;
window.cancelarPedido = cancelarPedido;