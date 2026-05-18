/**
 * compra.js
 * 
 * Utilitário para operações de compra (pedidos).
 * Fornece funções para criar pedidos e adicionar produtos com tratamento de autenticação.
 */

/**
 * Cria um novo pedido
 * @param {number} id_usuario - ID do usuário (cliente)
 * @param {number} valor_total - Valor total do pedido
 * @returns {Promise<Object>} - Dados do pedido criado ou erro
 */
async function criarPedido(id_usuario, valor_total) {
    try {
        const response = await fetch('/pedidos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Envia cookies (token)
            body: JSON.stringify({
                id_usuario,
                valor_total,
                status: 'pendente'
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao criar pedido');
        }

        return await response.json();
    } catch (error) {
        console.error('Erro ao criar pedido:', error);
        throw error;
    }
}

/**
 * Adiciona um produto a um pedido existente
 * @param {number} pedido_id - ID do pedido
 * @param {number} id_produto - ID do produto
 * @param {number} quantidade - Quantidade do produto
 * @returns {Promise<Object>} - Item do pedido criado ou erro
 */
async function adicionarProdutoAoPedido(pedido_id, id_produto, quantidade) {
    try {
        const response = await fetch(`/pedidos/${pedido_id}/itens`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Envia cookies (token)
            body: JSON.stringify({
                id_produto,
                quantidade
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao adicionar produto');
        }

        return await response.json();
    } catch (error) {
        console.error('Erro ao adicionar produto:', error);
        throw error;
    }
}

/**
 * Atualiza a quantidade de um produto em um pedido
 * @param {number} pedido_id - ID do pedido
 * @param {number} produto_id - ID do produto
 * @param {number} quantidade - Nova quantidade
 * @returns {Promise<Object>} - Item atualizado ou erro
 */
async function atualizarQuantidadeProduto(pedido_id, produto_id, quantidade) {
    try {
        const response = await fetch(`/pedidos/${pedido_id}/itens/${produto_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Envia cookies (token)
            body: JSON.stringify({
                quantidade
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao atualizar quantidade');
        }

        return await response.json();
    } catch (error) {
        console.error('Erro ao atualizar quantidade:', error);
        throw error;
    }
}

/**
 * Remove um produto de um pedido
 * @param {number} pedido_id - ID do pedido
 * @param {number} produto_id - ID do produto
 * @returns {Promise<void>}
 */
async function removerProdutoDoPedido(pedido_id, produto_id) {
    try {
        const response = await fetch(`/pedidos/${pedido_id}/itens/${produto_id}`, {
            method: 'DELETE',
            credentials: 'include', // Envia cookies (token)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao remover produto');
        }
    } catch (error) {
        console.error('Erro ao remover produto:', error);
        throw error;
    }
}

// Exporta funções globalmente
window.criarPedido = criarPedido;
window.adicionarProdutoAoPedido = adicionarProdutoAoPedido;
window.atualizarQuantidadeProduto = atualizarQuantidadeProduto;
window.removerProdutoDoPedido = removerProdutoDoPedido;
