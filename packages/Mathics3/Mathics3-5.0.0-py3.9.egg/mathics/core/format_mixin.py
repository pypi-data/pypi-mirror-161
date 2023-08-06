# -*- coding: utf-8 -*-
"""
Mix-in functions for formatting.

Classes in this module get added or "mixed in" to Atoms, or specific Atoms e.g. Symbol or Number
and Expressions in order to provide additional methods of some related variety such as
for formatting an object or for performing a numeric-related actiivty.

These methods have to be separate from the classes that mix them in
themselves for various reasons.

In the case of ``FormatFunctions``, this is because they pull in lots of
specific Symbol names. When we get Symbol as a unique name-only thing versus
Symbol as kind of variable or thing with a properties then we
might reconsider the use of this as a mix in.

"""

from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFullForm,
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolHoldForm,
    SymbolList,
    SymbolNumberForm,
    SymbolOutputForm,
    SymbolPostfix,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolStandardForm,
    format_symbols,
)


class FormatFunctions:
    """
    This is a mix-in class for Formatting an Element-like object.
    """

    def do_format(self, evaluation, form):
        """
        Applies formats associated to the expression and removes
        superfluous enclosing formats.
        """

        if isinstance(form, str):
            form = Symbol(form)
        formats = format_symbols

        evaluation.inc_recursion_depth()
        try:
            expr = self
            head = self.get_head()
            leaves = self.get_elements()
            include_form = False
            # If the expression is enclosed by a Format
            # takes the form from the expression and
            # removes the format from the expression.
            if head in formats and len(leaves) == 1:
                expr = leaves[0]
                if not (form is SymbolOutputForm and head is SymbolStandardForm):
                    form = head
                    include_form = True
            unformatted = expr
            # If form is Fullform, return it without changes
            if form is SymbolFullForm:
                if include_form:
                    expr = self.create_expression(form, expr)
                    expr.unformatted = unformatted
                return expr

            # Repeated and RepeatedNull confuse the formatter,
            # so we need to hardlink their format rules:
            if head is SymbolRepeated:
                if len(leaves) == 1:
                    return self.create_expression(
                        SymbolHoldForm,
                        self.create_expression(
                            SymbolPostfix,
                            self.create_expression(SymbolList, leaves[0]),
                            "..",
                            170,
                        ),
                    )
                else:
                    return self.create_expression(SymbolHoldForm, expr)
            elif head is SymbolRepeatedNull:
                if len(leaves) == 1:
                    return self.create_expression(
                        SymbolHoldForm,
                        self.create_expression(
                            SymbolPostfix,
                            self.create_expression(SymbolList, leaves[0]),
                            "...",
                            170,
                        ),
                    )
                else:
                    return self.create_expression(SymbolHoldForm, expr)

            # If expr is not an atom, looks for formats in its definition
            # and apply them.
            def format_expr(expr):
                if not (isinstance(expr, Atom)) and not (isinstance(expr.head, Atom)):
                    # expr is of the form f[...][...]
                    return None
                name = expr.get_lookup_name()
                formats = evaluation.definitions.get_formats(name, form.get_name())
                for rule in formats:
                    result = rule.apply(expr, evaluation)
                    if result is not None and result != expr:
                        return result.evaluate(evaluation)
                return None

            formatted = format_expr(expr)
            if formatted is not None:
                result = formatted.do_format(evaluation, form)
                if include_form:
                    result = self.create_expression(form, result)
                result.unformatted = unformatted
                return result

            # If the expression is still enclosed by a Format,
            # iterate.
            # If the expression is not atomic or of certain
            # specific cases, iterate over the leaves.
            head = expr.get_head()
            if head in formats:
                expr = expr.do_format(evaluation, form)
            elif (
                head is not SymbolNumberForm
                and not isinstance(expr, Atom)
                and head is not SymbolGraphics
                and head is not SymbolGraphics3D
            ):
                # print("Not inside graphics or numberform, and not is atom")
                new_elements = [
                    leaf.do_format(evaluation, form) for leaf in expr.leaves
                ]
                expr = self.create_expression(
                    expr.head.do_format(evaluation, form), *new_elements
                )

            if include_form:
                expr = self.create_expression(form, expr)
            expr.unformatted = unformatted
            return expr
        finally:
            evaluation.dec_recursion_depth()

    def format(self, evaluation, form, **kwargs) -> "BaseElement":
        """
        Applies formats associated to the expression, and then calls Makeboxes
        """
        from mathics.core.symbols import (
            Symbol,
            SymbolMakeBoxes,
        )

        if isinstance(form, str):
            form = Symbol(form)
        expr = self.do_format(evaluation, form)
        result = self.create_expression(SymbolMakeBoxes, expr, form).evaluate(
            evaluation
        )
        return result
