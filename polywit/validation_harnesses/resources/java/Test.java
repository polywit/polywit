public class Test {
  public static void main(String[] args) {
    try {
      Main.main(new String[0]);
      System.out.println("polywit: Witness Spurious");
    } catch (Exception e) {
      System.out.println(e);
      e.printStackTrace();
    }
  }
}