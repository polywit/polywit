fun main(args: Array<String>) {
    try {
        polywit_main(emptyArray<String>())
        println("polywit: Witness Spurious")
    } catch (e: AssertionError) {
        println(e)
        e.printStackTrace()
    }
}