package org.polywit.benchmarks

import java.util.Queue
import java.util.LinkedList

object Verifier {
    var assumptionList = emptyArray<String>()
    var assumptions: Queue<String> = LinkedList<String>()

    init {
        for (assumption in assumptionList) {
            assumptions.add(assumption)
        }
    }

    fun assume(condition: Boolean) {
        if (!condition) {
            Runtime.getRuntime().halt(1)
        }
    }

    fun nondetBoolean(): Boolean {
        val assumption: String = assumptions.remove()
        return assumption.toBoolean()
    }

    fun nondetByte(): Byte {
        val assumption: String = assumptions.remove()
        return assumption.toByte()
    }

    fun nondetChar(): Char {
        val assumption: String = assumptions.remove()
        return assumption.toInt().toChar()
    }

    fun nondetShort(): Short {
        val assumption: String = assumptions.remove()
        return assumption.toShort()
    }

    fun nondetInt(): Int {
        val assumption: String = assumptions.remove()
        return assumption.toInt()
    }

    fun nondetLong(): Long {
        val assumption: String = assumptions.remove()
        return assumption.toLong()
    }

    fun nondetFloat(): Float {
        val assumption: String = assumptions.remove()
        return assumption.toFloat()
    }

    fun nondetDouble(): Double {
        val assumption: String = assumptions.remove()
        return assumption.toDouble()
    }

    fun nondetString(): String {
        return assumptions.remove()
    }
}