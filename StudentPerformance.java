import java.util.ArrayList;
import java.util.Scanner;

class Student {
    String name;
    double total;
    double average;
    String grade;

    Student(String name, double total, double average, String grade) {
        this.name = name;
        this.total = total;
        this.average = average;
        this.grade = grade;
    }
}

public class StudentPerformance {

    // Method to calculate grade
    public static String calculateGrade(double avg) {
        if (avg >= 85) {
            return "A";
        } else if (avg >= 70) {
            return "B";
        } else if (avg >= 55) {
            return "C";
        } else {
            return "Fail";
        }
    }

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);
        ArrayList<Student> students = new ArrayList<>();

        System.out.print("Enter number of students: ");
        int n = sc.nextInt();

        for (int i = 0; i < n; i++) {
            sc.nextLine(); // consume newline
            System.out.println("\nEnter details for Student " + (i + 1));

            System.out.print("Name: ");
            String name = sc.nextLine();

            double total = 0;
            for (int j = 1; j <= 3; j++) {
                System.out.print("Enter mark " + j + ": ");
                total += sc.nextDouble();
            }

            double average = total / 3;
            String grade = calculateGrade(average);

            students.add(new Student(name, total, average, grade));
        }

        // Display report
        System.out.println("\n--- Student Report ---");
        for (Student s : students) {
            System.out.printf("%s | Total: %.2f | Avg: %.2f | Grade: %s\n",
                    s.name, s.total, s.average, s.grade);
        }

        // Find top performer
        Student topper = students.get(0);
        for (Student s : students) {
            if (s.total > topper.total) {
                topper = s;
            }
        }

        System.out.println("\n🏆 Top Performer: " + topper.name +
                " with " + topper.total + " marks");

        sc.close();
    }
}
