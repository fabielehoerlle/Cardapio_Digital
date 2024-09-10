import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv
from db import db_conectar, db_listarprodutos, db_listarpedidos

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class MenuItem:
    def __init__(self, id, name, description, price, image_path):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image_path = image_path

class RestaurantMenu(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Restaurante Delícia")
        self.geometry("400x600")
        self.configure(bg="#F3F4F6")

        # self.menu_items = [
        #     MenuItem(1, "X-Burger", "Hambúrguer com queijo, alface e tomate", 15.90, os.path.abspath("imagens/1.png")),
        #     MenuItem(2, "Batata Frita", "Porção de batata frita crocante", 8.50, os.path.abspath("imagens/2.jpg")),
        #     MenuItem(3, "Refrigerante", "Lata 350ml", 5.00, os.path.abspath("imagens/3.jpeg")),
        # ]
        produtos = db_listarprodutos()
        self.menu_items = []
        for produto in produtos:
            img = produto["imagem"] if produto["imagem"] else "imagens/0.png"
            self.menu_items.append(MenuItem(produto["id"], produto["nome"], produto["descricao"], produto["preco"], os.path.abspath(img)))

        self.cart_items = {}
        self.payment_methods = ["Cartão de Crédito", "Cartão de Débito", "Pix", "Dinheiro"]

        # Adicionar histórico de pedidos fictício
        self.order_history = db_listarpedidos()

        # Estabelecer conexão com o banco de dados
        self.db_connection = db_conectar()
        if not self.db_connection:
            print("Não foi possível conectar ao banco de dados. O aplicativo pode não funcionar corretamente.")

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#DC2626", pady=10)
        header.pack(fill=tk.X)

        title = tk.Label(header, text="Restaurante Delícia", font=("Arial", 16, "bold"), bg="#DC2626", fg="white")
        title.pack(side=tk.LEFT, padx=10)

        # Adicionar botão de histórico
        history_button = tk.Button(header, text="Histórico", bg="white", fg="#DC2626", font=("Arial", 12), padx=10, pady=5, command=self.open_history)
        history_button.pack(side=tk.RIGHT, padx=10)

        # Main content
        main_content = tk.Frame(self, bg="#F3F4F6")
        main_content.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_content, bg="#F3F4F6")
        scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F3F4F6")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for item in self.menu_items:
            self.create_menu_item_widget(scrollable_frame, item)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Footer
        footer = tk.Frame(self, bg="white", pady=10)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.total_items_label = tk.Label(footer, text="Total de itens: 0", font=("Arial", 12, "bold"), bg="white")
        self.total_items_label.pack(side=tk.LEFT, padx=10)

        view_cart_button = tk.Button(footer, text="Ver carrinho", bg="#DC2626", fg="white", font=("Arial", 12), padx=10, pady=5, command=self.open_cart)
        view_cart_button.pack(side=tk.RIGHT, padx=10)

    def create_menu_item_widget(self, parent, item):
        frame = tk.Frame(parent, bg="white", pady=10, padx=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Imagem do item
        image = self.load_image(item.image_path)
        image_label = tk.Label(frame, image=image, bg="white")
        image_label.image = image
        image_label.grid(row=0, column=0, rowspan=3, padx=(0, 10))

        # Nome do item
        name_label = tk.Label(frame, text=item.name, font=("Arial", 12, "bold"), bg="white")
        name_label.grid(row=0, column=1, sticky="w")

        # Descrição do item
        description_label = tk.Label(frame, text=item.description, font=("Arial", 10), bg="white", wraplength=200)
        description_label.grid(row=1, column=1, sticky="w")

        # Preço do item
        price_label = tk.Label(frame, text=f"R$ {item.price:.2f}", font=("Arial", 10, "bold"), fg="#DC2626", bg="white")
        price_label.grid(row=2, column=1, sticky="w")

        # Botões de adicionar/remover
        button_frame = tk.Frame(frame, bg="white")
        button_frame.grid(row=0, column=2, rowspan=3, padx=(10, 0))

        minus_button = tk.Button(button_frame, text="-", command=lambda: self.remove_from_cart(item), bg="#DC2626", fg="white", font=("Arial", 12, "bold"))
        minus_button.grid(row=0, column=0)

        self.cart_items[item.id] = tk.StringVar(value="0")
        quantity_label = tk.Label(button_frame, textvariable=self.cart_items[item.id], width=3, font=("Arial", 12), bg="white")
        quantity_label.grid(row=0, column=1)

        plus_button = tk.Button(button_frame, text="+", command=lambda: self.add_to_cart(item), bg="#DC2626", fg="white", font=("Arial", 12, "bold"))
        plus_button.grid(row=0, column=2)

    def load_image(self, path):
        try:
            img = Image.open(path)
            img = img.resize((80, 80), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Erro ao carregar a imagem {path}: {e}")
            # Retorna uma imagem placeholder ou None
            return None

    def add_to_cart(self, item):
        current = int(self.cart_items[item.id].get())
        self.cart_items[item.id].set(str(current + 1))
        self.update_total_items()

    def remove_from_cart(self, item):
        current = int(self.cart_items[item.id].get())
        if current > 0:
            self.cart_items[item.id].set(str(current - 1))
            self.update_total_items()

    def update_total_items(self):
        total = sum(int(value.get()) for value in self.cart_items.values())
        self.total_items_label.config(text=f"Total de itens: {total}")

    def open_cart(self):
        cart_window = tk.Toplevel(self)
        cart_window.title("Carrinho")
        cart_window.geometry("400x500")
        cart_window.configure(bg="#F3F4F6")

        # Itens no carrinho
        items_frame = tk.Frame(cart_window, bg="#F3F4F6")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        total_price = 0
        for item in self.menu_items:
            quantity = int(self.cart_items[item.id].get())
            if quantity > 0:
                item_frame = tk.Frame(items_frame, bg="white", pady=5)
                item_frame.pack(fill=tk.X, pady=2)

                tk.Label(item_frame, text=f"{item.name} x{quantity}", bg="white", font=("Arial", 12)).pack(side=tk.LEFT)
                tk.Label(item_frame, text=f"R$ {item.price * quantity:.2f}", bg="white", font=("Arial", 12)).pack(side=tk.RIGHT)

                total_price += item.price * quantity

        tk.Label(items_frame, text=f"Total: R$ {total_price:.2f}", bg="#F3F4F6", font=("Arial", 14, "bold")).pack(pady=10)

        # Seleção de forma de pagamento
        payment_frame = tk.Frame(cart_window, bg="#F3F4F6")
        payment_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(payment_frame, text="Forma de Pagamento:", bg="#F3F4F6", font=("Arial", 12)).pack(side=tk.LEFT)
        payment_var = tk.StringVar(value=self.payment_methods[0])
        payment_select = ttk.Combobox(payment_frame, textvariable=payment_var, values=self.payment_methods, state="readonly")
        payment_select.pack(side=tk.RIGHT)

        # Botão para concluir compra
        finish_button = tk.Button(cart_window, text="Concluir Compra", bg="#DC2626", fg="white", font=("Arial", 12), padx=10, pady=5, command=lambda: self.finish_purchase(cart_window))
        finish_button.pack(pady=20)

    def finish_purchase(self, cart_window):
        cart_window.destroy()
        success_window = tk.Toplevel(self)
        success_window.title("Compra Concluída")
        success_window.geometry("300x150")
        success_window.configure(bg="#F3F4F6")

        tk.Label(success_window, text="Compra realizada com sucesso!", bg="#F3F4F6", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Button(success_window, text="OK", bg="#DC2626", fg="white", font=("Arial", 12), command=success_window.destroy).pack()

    def open_history(self):
        history_window = tk.Toplevel(self)
        history_window.title("Histórico de Pedidos")
        history_window.geometry("500x400")
        history_window.configure(bg="#F3F4F6")

        # Cabeçalho
        header = tk.Frame(history_window, bg="#DC2626", pady=10)
        header.pack(fill=tk.X)

        title = tk.Label(header, text="Histórico de Pedidos", font=("Arial", 16, "bold"), bg="#DC2626", fg="white")
        title.pack()

        # Lista de pedidos
        history_frame = tk.Frame(history_window, bg="#F3F4F6")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cabeçalho da lista
        headers = ["ID", "Data", "descricao", "Total"]
        for i, header in enumerate(headers):
            tk.Label(history_frame, text=header, bg="#F3F4F6", font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        # Exibir pedidos
        for i, order in enumerate(self.order_history, start=1):
            tk.Label(history_frame, text=str(order["id"]), bg="#F3F4F6").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            tk.Label(history_frame, text=order["data"], bg="#F3F4F6").grid(row=i, column=1, padx=5, pady=2, sticky="w")
            tk.Label(history_frame, text=order["descricao"], bg="#F3F4F6").grid(row=i, column=2, padx=5, pady=2, sticky="w")
            tk.Label(history_frame, text=f"R$ {order['total']:.2f}", bg="#F3F4F6").grid(row=i, column=3, padx=5, pady=2, sticky="w")

        # Botão para fechar
        close_button = tk.Button(history_window, text="Fechar", bg="#DC2626", fg="white", font=("Arial", 12), padx=10, pady=5, command=history_window.destroy)
        close_button.pack(pady=20)

    def __del__(self):
        # Fechar a conexão com o banco de dados quando o objeto for destruído
        if hasattr(self, 'db_connection') and self.db_connection:
            self.db_connection.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    app = RestaurantMenu()
    app.mainloop()