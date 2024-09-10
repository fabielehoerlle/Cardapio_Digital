import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import psycopg2
import os

# Função para conectar ao banco de dados
def connect_db():
    try:
        connection = psycopg2.connect(
            dbname="cardapio",
            user="postgres",
            password="Isatkm3098*",
            host="localhost"
        )
        return connection
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para carregar produtos
def load_products():
    connection = connect_db()
    if connection is None:
        return []
    cursor = connection.cursor()
    cursor.execute("SELECT id, nome, descricao, preco, estoque, imagem FROM produtos")
    products = cursor.fetchall()
    connection.close()
    return products

# Função para exibir produtos
def display_products():
    products = load_products()
    if products:
        product_list.delete(0, tk.END)
        product_images.clear()
        for product in products:
            display_text = f"{product[1]} - R${product[3]:.2f} ({product[4]} em estoque)"
            product_list.insert(tk.END, display_text)
            image_path = product[5]
            if os.path.isfile(image_path):
                image = Image.open(image_path)
                image = image.resize((100, 100))  # Redimensionar a imagem
                photo = ImageTk.PhotoImage(image)
                product_images.append((photo, product[0]))  # Armazenar imagem e id do produto
            else:
                product_images.append((None, product[0]))  # Nenhuma imagem encontrada

        # Atualizar o display da imagem selecionada
        product_list.bind("<<ListboxSelect>>", update_image_display)

# Função para atualizar a imagem do produto selecionado
def update_image_display(event):
    try:
        selected_index = product_list.curselection()[0]
        _, product_id = product_images[selected_index]
        for img, p_id in product_images:
            if p_id == product_id:
                if img:
                    image_label.config(image=img)
                    image_label.image = img
                else:
                    image_label.config(image='')
                    image_label.image = None
                break
    except IndexError:
        pass

# Função para realizar um pedido
def place_order():
    products = load_products()
    if not products:
        messagebox.showwarning("Pedido", "Não há produtos disponíveis para pedido.")
        return
    
    order_items = []
    total = 0

    while True:
        product_id = simpledialog.askinteger("Pedido", "Digite o ID do produto (ou 0 para finalizar):")
        if product_id == 0:
            break
        
        quantity = simpledialog.askinteger("Pedido", "Digite a quantidade:")
        if quantity is None:
            break
        
        # Verificar se o produto existe e se há estoque suficiente
        product = next((p for p in products if p[0] == product_id), None)
        if not product:
            messagebox.showwarning("Pedido", f"Produto com ID {product_id} não encontrado.")
            continue
        
        if product[4] < quantity:
            messagebox.showwarning("Pedido", f"Estoque insuficiente para o produto {product[1]}.")
            continue
        
        subtotal = product[3] * quantity
        order_items.append((product_id, quantity, subtotal))
        total += subtotal
    
    if not order_items:
        messagebox.showwarning("Pedido", "Nenhum item adicionado ao pedido.")
        return
    
    connection = connect_db()
    if connection is None:
        return
    
    cursor = connection.cursor()
    cursor.execute("INSERT INTO pedidos (total) VALUES (%s) RETURNING id", (total,))
    order_id = cursor.fetchone()[0]
    
    for item in order_items:
        cursor.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, subtotal) VALUES (%s, %s, %s, %s)", 
                       (order_id, item[0], item[1], item[2]))
        # Atualizar estoque
        cursor.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (item[1], item[0]))
    
    connection.commit()
    connection.close()
    
    messagebox.showinfo("Pedido", f"Pedido realizado com sucesso! ID do pedido: {order_id}. Total: R${total:.2f}")

# Função para gerenciar pagamentos
def manage_payments():
    order_id = simpledialog.askinteger("Pagamento", "Digite o ID do pedido:")
    if not order_id:
        return
    
    connection = connect_db()
    if connection is None:
        return
    
    cursor = connection.cursor()
    cursor.execute("SELECT total, pago FROM pedidos WHERE id = %s", (order_id,))
    result = cursor.fetchone()
    
    if not result:
        messagebox.showwarning("Pagamento", "Pedido não encontrado.")
        connection.close()
        return
    
    total, paid = result
    if paid:
        messagebox.showinfo("Pagamento", "Este pedido já está pago.")
    else:
        cursor.execute("UPDATE pedidos SET pago = TRUE WHERE id = %s", (order_id,))
        connection.commit()
        messagebox.showinfo("Pagamento", f"Pagamento realizado com sucesso! Total: R${total:.2f}")
    
    connection.close()

# Criação da interface Tkinter
root = tk.Tk()
root.title("Cardápio Digital - Doceria")

# Listagem de produtos
product_list = tk.Listbox(root, width=60, height=15)
product_list.pack(pady=10)

# Label para exibir imagens
image_label = tk.Label(root)
image_label.pack(pady=10)

# Lista para armazenar imagens e IDs dos produtos
product_images = []

# Botão para carregar produtos
load_button = tk.Button(root, text="Carregar Produtos", command=display_products)
load_button.pack(pady=5)

# Botão para realizar pedido
order_button = tk.Button(root, text="Realizar Pedido", command=place_order)
order_button.pack(pady=5)

# Botão para gerenciar pagamentos
payment_button = tk.Button(root, text="Gerenciar Pagamentos", command=manage_payments)
payment_button.pack(pady=5)

root.mainloop()
