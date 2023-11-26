import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {

    public static void main(String[] args) {
        // JDBC URL, username, and password of MySQL server
        String url = "jdbc:mysql://localhost:3306/mydatabase";
        String user = "username";
        String password = "secure_password"; // A secure password should be used

        try {
            // Establish a connection
            Connection connection = DriverManager.getConnection(url, user, password);

            // Perform database operations...

            // Close the connection
            connection.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
