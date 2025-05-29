#!/usr/bin/python3
"""
Focus Reader Console
This is a command-line interpreter for managing books, users,
reading goals, and highlights.
"""

import cmd
import os
import sys
import django
import re
import json
import csv

# Initialize Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure script finds Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Adjust if needed
django.setup()

from api.models import User, Book, ReadingGoal, Highlight  # Import models after setup

class FocusReaderCommand(cmd.Cmd):
    """Command-line interface for managing Codexia backend."""
    
    prompt = "(focus_reader) "

    objects = {
        'User': User,
        'Book': Book,
        'ReadingGoal': ReadingGoal,
        'Highlight': Highlight
    }

    def do_quit(self, args):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, args):
        """EOF command to exit the program."""
        print()
        return True

    def emptyline(self):
        """Handle empty input (do nothing)."""
        pass

    ### 🆕 CREATE ###
    def do_create(self, args):
        """Create a new instance: create <ClassName> <key=value> ..."""
        tokens = args.split()
        if not tokens:
            print("** class name missing **")
            return

        class_name = tokens[0]
        if class_name not in self.objects:
            print("** class doesn't exist **")
            return

        obj = self.objects[class_name]()  # Create instance

        # Extract parameters
        param_pattern = re.compile(r'(\w+)=(".*?"|\S+)')
        params = dict(param_pattern.findall(args))

        for key, value in params.items():
            value = value.strip('"')  # Remove quotes
            if key in ["user", "user_id"]:  # Handle ForeignKey (User)
                try:
                    value = User.objects.get(id=int(value))  # Convert to User instance
                except User.DoesNotExist:
                    print(f"❌ Error: User with ID {value} does not exist.")
                    return
            setattr(obj, key, value)

        obj.save()
        print(f"✅ Created {class_name}: {obj.id}")

    ### 📌 SHOW ###
    def do_show(self, args):
        """Show an instance: show <ClassName> <id>"""
        tokens = args.split()
        if len(tokens) < 2:
            print("** instance id missing **")
            return
        
        class_name, obj_id = tokens
        if class_name not in self.objects:
            print("** class doesn't exist **")
            return

        obj = self.objects[class_name].objects.filter(id=obj_id).first()
        if not obj:
            print("** no instance found **")
        else:
            print(obj)

    ### ❌ DESTROY ###
    def do_destroy(self, args):
        """Delete an instance: destroy <ClassName> <id>"""
        tokens = args.split()
        if len(tokens) < 2:
            print("** instance id missing **")
            return

        class_name, obj_id = tokens
        if class_name not in self.objects:
            print("** class doesn't exist **")
            return

        obj = self.objects[class_name].objects.filter(id=obj_id).first()
        if not obj:
            print("** no instance found **")
        else:
            obj.delete()
            print(f"🗑️ Deleted {class_name} {obj_id}")

    ### 🔍 SEARCH BOOKS ###
    def do_search_books(self, arg):
        """Search for books by title. Usage: search_books "title keyword" """
        if not arg:
            print("❌ Error: Provide a title keyword to search.")
            return
        
        books = Book.objects.filter(title__icontains=arg)
        
        if not books:
            print(f"ℹ️ No books found matching '{arg}'.")
            return
        
        print(f"🔍 Books matching '{arg}':")
        for book in books:
            print(f"- {book.title} by {book.author} (User: {book.user.email})")

    ### 📚 LIST USER BOOKS ###
    def do_user_books(self, arg):
        """List all books belonging to a specific user. Usage: user_books user_id [title]"""
        args = arg.split()
        if not args or not args[0].isdigit():
            print("❌ Error: You must provide a valid user ID.")
            return
        
        user_id = int(args[0])
        title_filter = " ".join(args[1:]) if len(args) > 1 else None

        try:
            user = User.objects.get(id=user_id)
            books = Book.objects.filter(user=user)

            if title_filter:
                books = books.filter(title__icontains=title_filter)

            if not books:
                print(f"ℹ️ No books found for user {user.email} (ID: {user_id})")
                return
            
            print(f"📚 Books for {user.email} (ID: {user_id}):")
            for book in books:
                print(f"- {book.title} by {book.author}")
        
        except User.DoesNotExist:
            print(f"❌ Error: User with ID {user_id} does not exist.")

    ### 📖 LIST USERS WITH BOOKS ###
    def do_users_with_books(self, arg):
        """List all users who own books. Usage: users_with_books"""
        users = User.objects.filter(book__isnull=False).distinct()

        if not users:
            print("ℹ️ No users have books.")
            return

        print("📖 Users who own books:")
        for user in users:
            print(f"- {user.email} ({user.id})")

    ### 🎯 USER READING GOALS ###
    def do_user_goals(self, arg):
        """Show reading goals for a user. Usage: user_goals user_id"""
        if not arg.isdigit():
            print("❌ Error: User ID must be a number.")
            return

        user_id = int(arg)

        try:
            user = User.objects.get(id=user_id)
            goals = ReadingGoal.objects.filter(user=user)

            if not goals:
                print(f"ℹ️ No reading goals set for {user.email} (ID: {user_id}).")
                return

            print(f"🎯 Reading goals for {user.email} (ID: {user_id}):")
            for goal in goals:
                print(f"- {goal.target_books} books by {goal.deadline}")
        
        except User.DoesNotExist:
            print(f"❌ Error: User with ID {user_id} does not exist.")

    ### 📂 EXPORT DATA ###
    def do_export(self, arg):
        """Export model data. Usage: export ModelName format=json/csv"""
        args = arg.split()
        if len(args) != 2:
            print("❌ Error: Usage: export ModelName format=json/csv")
            return

        model_name, file_format = args
        try:
            model = globals()[model_name]  # Get model class dynamically
            data = list(model.objects.values())

            with open(f"{model_name}.{file_format}", "w") as f:
                if file_format == "json":
                    json.dump(data, f, indent=4)
                elif file_format == "csv":
                    writer = csv.writer(f)
                    writer.writerow(data[0].keys())  # Header
                    for row in data:
                        writer.writerow(row.values())

            print(f"✅ Data exported to {model_name}.{file_format} successfully.")
        except KeyError:
            print(f"❌ Error: Model '{model_name}' does not exist.")

if __name__ == "__main__":
    FocusReaderCommand().cmdloop()
