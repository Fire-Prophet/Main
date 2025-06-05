using System;
using System.Collections.Generic;
using System.Linq; // LINQ 확장 메서드를 사용하기 위함

public class Book
{
    // 속성 정의 (Property)
    public string Title { get; set; }
    public string Author { get; set; }
    public int PublicationYear { get; set; }
    public string Isbn { get; private set; } // ISBN은 생성 시 한 번만 설정 가능

    // 생성자 (Constructor)
    public Book(string title, string author, int year, string isbn)
    {
        Title = title;
        Author = author;
        PublicationYear = year;
        Isbn = isbn;
        Console.WriteLine($"새로운 책이 생성되었습니다: '{Title}' by {Author}");
    }

    // 메서드 (Method)
    public void DisplayBookInfo()
    {
        Console.WriteLine($"\n--- 도서 정보 ---");
        Console.WriteLine($"제목: {Title}");
        Console.WriteLine($"저자: {Author}");
        Console.WriteLine($"출판 연도: {PublicationYear}");
        Console.WriteLine($"ISBN: {Isbn}");
        Console.WriteLine($"-----------------");
    }
}

public class Bookstore
{
    private List<Book> books; // 책들을 저장할 리스트

    public Bookstore()
    {
        books = new List<Book>();
        Console.WriteLine("서점이 문을 열었습니다!");
    }

    public void AddBook(Book book)
    {
        books.Add(book);
        Console.WriteLine($"'{book.Title}'이(가) 서점에 추가되었습니다.");
    }

    public void ListAllBooks()
    {
        if (!books.Any()) // LINQ의 Any() 확장 메서드 사용
        {
            Console.WriteLine("서점에 책이 없습니다.");
            return;
        }

        Console.WriteLine("\n=== 서점 내 모든 책 목록 ===");
        foreach (var book in books)
        {
            book.DisplayBookInfo();
        }
        Console.WriteLine("===========================");
    }

    public Book FindBookByTitle(string title)
    {
        // LINQ의 FirstOrDefault() 확장 메서드 사용
        return books.FirstOrDefault(b => b.Title.Equals(title, StringComparison.OrdinalIgnoreCase));
    }
}

public class Program
{
    public static void Main(string[] args)
    {
        Bookstore myBookstore = new Bookstore();

        // 새 책 객체 생성
        Book book1 = new Book("데미안", "헤르만 헤세", 1919, "978-89-324-1111-1");
        Book book2 = new Book("어린 왕자", "앙투안 드 생텍쥐페리", 1943, "978-89-324-2222-2");
        Book book3 = new Book("1984", "조지 오웰", 1949, "978-89-324-3333-3");

        // 서점에 책 추가
        myBookstore.AddBook(book1);
        myBookstore.AddBook(book2);
        myBookstore.AddBook(book3);

        // 모든 책 목록 표시
        myBookstore.ListAllBooks();

        // 특정 책 찾기
        string searchTitle = "어린 왕자";
        Book foundBook = myBookstore.FindBookByTitle(searchTitle);
        if (foundBook != null)
        {
            Console.WriteLine($"\n'{searchTitle}'을(를) 찾았습니다:");
            foundBook.DisplayBookInfo();
        }
        else
        {
            Console.WriteLine($"\n'{searchTitle}' 책을 찾을 수 없습니다.");
        }

        Console.WriteLine("\n프로그램 종료.");
    }
}
