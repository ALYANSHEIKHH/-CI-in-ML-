import streamlit as st
import json
import pandas as pd
import plotly.express as px

# ✅ Fix: Ensure set_page_config() is the first Streamlit command

st.set_page_config(page_title="Library Collection", layout="wide")

class BookCollection:
    def __init__(self):
        self.book_list = []
        self.storage_file = "books_data.json"
        self.read_from_file()

    def read_from_file(self):
        try:
            with open(self.storage_file, "r") as file:
                self.book_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.book_list = []

    def save_to_file(self):
        with open(self.storage_file, "w") as file:
            json.dump(self.book_list, file, indent=4)

    def create_new_book(self, title, author, year, genre, read):
        new_book = {
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "read": read,
        }
        self.book_list.append(new_book)
        self.save_to_file()

    def delete_book(self, title):
        self.book_list = [book for book in self.book_list if book["title"].lower() != title.lower()]
        self.save_to_file()

    def find_books(self, search_text):
        return [book for book in self.book_list if search_text.lower() in book["title"].lower() or search_text.lower() in book["author"].lower()]

    def update_book(self, title, new_title, new_author, new_year, new_genre, new_read):
        for book in self.book_list:
            if book["title"].lower() == title.lower():
                book.update({
                    "title": new_title or book["title"],
                    "author": new_author or book["author"],
                    "year": new_year or book["year"],
                    "genre": new_genre or book["genre"],
                    "read": new_read if new_read is not None else book["read"]
                })
                self.save_to_file()
                return True
        return False

    def get_all_books(self):
        return self.book_list

    def get_reading_progress(self):
        total_books = len(self.book_list)
        completed_books = sum(1 for book in self.book_list if book["read"])
        return total_books, (completed_books / total_books * 100) if total_books > 0 else 0

# Streamlit UI
st.title("📚 Library Collection Manager")
st.sidebar.header("Navigation")
book_manager = BookCollection()
menu = st.sidebar.radio("Select an Option", ["Add Book", "View Books", "Search Books", "Update Book", "Delete Book", "Reading Progress"])

if menu == "Add Book":
    st.subheader("📖 Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        year = st.text_input("Publication Year")
        genre = st.text_input("Genre")
        read = st.checkbox("Have you read this book?")
        submitted = st.form_submit_button("➕ Add Book")
        if submitted and title and author:
            book_manager.create_new_book(title, author, year, genre, read)
            st.success("✅ Book added successfully!")

elif menu == "View Books":
    st.subheader("📚 Your Book Collection")
    books = book_manager.get_all_books()
    if books:
        df = pd.DataFrame(books)
        st.dataframe(df)
    else:
        st.info("No books in the collection.")

elif menu == "Search Books":
    st.subheader("🔍 Search for a Book")
    search_query = st.text_input("Enter title or author name")
    if search_query:
        results = book_manager.find_books(search_query)
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df)
        else:
            st.warning("No matching books found.")

elif menu == "Update Book":
    st.subheader("✏️ Update Book Details")
    title = st.text_input("Enter the title of the book you want to update")
    if title:
        new_title = st.text_input("New Title")
        new_author = st.text_input("New Author")
        new_year = st.text_input("New Publication Year")
        new_genre = st.text_input("New Genre")
        new_read = st.checkbox("Mark as Read?")
        if st.button("Update Book"):
            success = book_manager.update_book(title, new_title, new_author, new_year, new_genre, new_read)
            if success:
                st.success("✅ Book updated successfully!")
            else:
                st.warning("❌ Book not found!")

elif menu == "Delete Book":
    st.subheader("🗑️ Delete a Book")
    title = st.text_input("Enter the title of the book to delete")
    if st.button("Delete Book") and title:
        book_manager.delete_book(title)
        st.success("✅ Book deleted successfully!")

elif menu == "Reading Progress":
    st.subheader("📊 Reading Progress")
    total_books, completion_rate = book_manager.get_reading_progress()
    st.write(f"**Total books:** {total_books}")
    st.write(f"**Reading progress:** {completion_rate:.2f}%")
    
    if total_books > 0:
        df = pd.DataFrame({"Status": ["Read", "Unread"], "Count": [completion_rate, 100 - completion_rate]})
        fig = px.pie(df, values="Count", names="Status", title="Reading Progress", color_discrete_sequence=["#00cc96", "#636efa"])
        st.plotly_chart(fig)