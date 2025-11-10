# Comentarios P0 Susana - 31 Ocutubre 

Nota: 0,4 (sobre 0,5)

Se incluyen a continuación algunos comentarios/errores:
- El modelo DFM no se corresponde con la descripción realizada antes de las dimensiones (se incluyen atributos en la descripción que luego no se incluyen en el DFM, como los correspondientes a eventos y meteorología).
- Sería más recomendable que hospedador y ubicación se relacionasen directamente con el hecho. Esto evitaría tener un esquema en copo de nieve (aunque esta parte debe decidirse y justificarse en la tarea 2, no en esta).
- No se entiende lo descrito para los multivaluados (Se habla de que una de las ventajas de tener multivaluados es que "evita crear dimensións adicionais e táboas ponte
que complicarían o modelo sen aportar valor analítico significativo no contexto das nosas consultas". Si se añade multivaluado se representará con tablas puente (aunque esto no debe mencionarse aquí, sino en la tarea 2). Pero representar o no atributos multivaluados no es una decisión que se pueda tomar (o se tienen esos atributos o no se tienen).
- La decisión de usar SCD1 para los atributos del hospedador es incorrecta. Si tiene valoro analítico no se puede sobreescribir.
- Con valorador también debe usarse SCD2 para la edad (cualquier otra opción es incorrecta).
- Tal como se muestra en el DFM, lluvia y eventos serían degeneradas (o incluir como junk dimension dependiendo de la cardinalidad). Esto no sería así si tuviese los atributos descritos en la sección 3.1, pero no queda claro con el diagrama incluido.
