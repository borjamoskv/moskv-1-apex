## CAPÍTULO 2: LATENCIA EN LA TRINCHERA DE USERA

```yaml
Claim: Enlace de baja frecuencia establecido entre el nodo Uribarri y el subnodo Usera-01.
Proof: { Base: [0x8F2A_99B4], Range: [Usera, Uribarri], Confidence: [C5-REAL] }
```

El sótano de Marcelo Usera olía a una mezcla nauseabunda de humedad centenaria, fritanga de calamares del bar de la esquina y disolvente de PVC. Vicentín, sentado sobre un taburete cojo que amenazaba con descoyuntarse en cada respiración, observaba el monitor CRT con la devoción cansada de un monje en su scriptorium. Llevaba puesto un chándal de táctel azul eléctrico que emitía un crujido estático cada vez que se movía, una sinfonía de microdescargas que, según él, ayudaba a estabilizar el campo electromagnético del clúster de PlayStation 3 puenteadas que zumbaba a sus pies.

—Richi —masculló Vicentín, sin apartar la vista del fósforo ámbar—. Richi, que esto no tira. La latencia hacia el norte está subiendo más rápido que el precio de los churros en la Plaza Mayor. Estamos en 450 milisegundos. Eso no es un ping, es una carta certificada mandada por correo ordinario, aivalahostia.

El Richi, con un Ducados pegado al labio inferior y la mirada perdida entre las tripas abiertas de un switch Cisco de la época de las Olimpiadas de Barcelona, soltó un bufido.

—No me des la brasa, Vicentín, que estoy intentando crimpar un cable RJ-45 con los dientes porque el Patxi se llevó la crimpadora buena a Bilbao. Dice que allí la fibra es más dura y que las de plástico de aquí son para afeminados. 

—Pues dile al Patxi de mi parte que, por muy vasco que sea, la física es la física. Si no bajamos la resistencia en el puente de Pancorbo, los tensores de la matriz de atención se nos van a desalinear y la IA va a empezar a hablarnos en arameo o, peor aún, a recomendarnos podcasts de autoayuda. Que ya le vale, al viejuno.

Richi escupió una brizna de tabaco negro y se acercó a la terminal. El zumbido de los ventiladores de las PS3 era un coro de motores fuera de borda intentando cruzar el charco de la entropía. Tecleó `ping 19.168.1.100` —la IP del nodo de Uribarri—. Las respuestas caían con la desgana de un funcionario de ventanilla:

```bash
64 bytes from 19.168.1.100: icmp_seq=1 ttl=64 time=452 ms
64 bytes from 19.168.1.100: icmp_seq=2 ttl=64 time=489 ms
64 bytes from 19.168.1.100: icmp_seq=3 ttl=64 time=512 ms
```

—Es el Patxi —sentenció Richi, rascándose la nuca sucia—. Ha vuelto a activar el cortafuegos de nivel 2 con la tabla de enrutamiento estocástica que compiló el mes pasado bajo los efectos del patxaran con LSD. Voy a abrir canal de VoIP antes de que el buffer se sature y nos haga un core dump en los riñones.

Pulsó el switch físico de la consola de comunicaciones, un trasto fabricado con la carcasa de un walkie-talkie y una toma de antena de televisión analógica. Tras una ráfaga de estática que sonó como una lija frotando el cráneo de Vicentín, la voz de Patxi irrumpió en el sótano, nítida, cargada de ese cinismo ilustrado y seco de quien ha depurado sistemas operativos en tarjetas perforadas antes de que sus interlocutores supieran limpiarse los mocos.

—*¿Qué pasa, muchachada del sur?* —dijo Patxi, y de fondo se escuchó el click metálico de un mechero Zippo y el siseo del sirimiri sobre la claraboya de Uribarri—. *¿Ya os estáis ahogando en vuestra propia latencia? Os he dicho mil veces que el enrutamiento por defecto en Madrid es una cloaca de metadatos corporativos. Si no puenteáis el gateway de la UCO usando el payload asimétrico que os dejé en el directorio `/tmp`, vuestros paquetes van a seguir dando vueltas por los servidores de Telefónica como curas en un burdel.*

Vicentín se acercó al micrófono improvisado, arrastrando las botas de seguridad.

—¡Aúpa, Patxi! Que el payload ese está obsoleto, abuelo. Que le metí el linter y me dio más advertencias de seguridad que un manual de pirotecnia casera. Que nos van a capar la IP los de la Ertzaintza antes de que crucemos el Ebro.

Se oyó una risa seca de Patxi, una carcajada corta, inteligente y afilada como un bisturí.

—*Vicentín, alma de cántaro, eres más inocente que el mecanismo de un chupete* —replicó Patxi—. *El linter detecta vulnerabilidades porque está diseñado por ingenieros de Silicon Valley que se mean encima si ven un puntero sin inicializar. En la trinchera del C5-REAL, la vulnerabilidad es nuestra mayor exergía. Ese "fallo" de desbordamiento de buffer en la pila de red es precisamente lo que nos permite saltarnos la inspección profunda de paquetes del nodo del Gobierno Vasco. Es topología cuántica aplicada, gañán. El Txema cree que es magia, pero es simple álgebra lineal de bajo nivel. He modificado el kernel de las PS3 para que interpreten la latencia no como un retraso, sino como un parámetro de compresión termodinámica. Cuanto más tardan en llegar los paquetes, más densos se vuelven.*

Richi miró a Vicentín con las cejas arqueadas. El viejo Patxi era un bruto con boina y olor a tabaco negro, sí, pero su cerebro procesaba en ensamblador con la precisión de un mainframe de la Guerra Fría. No había un administrador de sistemas en toda la península que tuviera su nivel de malicia técnica. Tenemos cuarenta años ya, cojones. Yo nací el mismo día que Paquirrín, un glorioso 9 de febrero de 1984, y Patxi llegó al mundo cinco días más tarde del día de los enamorados, el 19. Es mi mejor amigo desde primero de EGB. Hemos compartido pupitre, peleas a pedradas, sobredosis de cafeína y mudanzas de servidores a las tres de la mañana. No hay nadie más rápido tirando líneas en C.

—¿Y el Txema? —preguntó Richi—. ¿Está estabilizando el voltaje?

—*El Txema está intentando enfriar el rack del sótano echándole nitrógeno líquido a una olla de alubias para ver si la superconductividad nos ahorra tres ciclos de reloj* —gruñó Patxi, y se oyó de fondo un juramento en vasco y el ruido de una cacerola cayendo al suelo—. *Ya le he dicho que si la temperatura baja de menos setenta, la grasa térmica de las GPUs se va a cristalizar y vamos a tener un bonito pisapapeles de silicio de tres mil euros. Pero ya sabéis cómo es: tiene más cabezonería que megas de caché. Haced el bypass que os he dicho, meted la directiva en el sysctl y dejad de llorar por la latencia. Nos vemos en el latente.*

La comunicación se cortó con un chasquido seco. 

Vicentín miró las gachas cuánticas que burbujeaban en el hornillo de camping gas, su color fluorescente reflejándose en las lentes de sus gafas pegadas con celo.

—Pues tiene razón el viejuno, Richi —admitió, cogiendo una cuchara de madera—. El Patxi es un cabrón, pero cuando abre la boca, compila. Venga, mete los comandos del bypass antes de que nos entre el *timeout* existencial y nos quedemos aquí tiesos mirando el gotelé.

Richi asintió, encendió otro Ducados con la brasa del anterior, y sus dedos volvieron a golpear las teclas. La trinchera estaba lista. La latencia empezaba a bajar.

```bash
64 bytes from 19.168.1.100: icmp_seq=4 ttl=64 time=12 ms (BYPASS ENGAGED)
```

—A funcionar —susurró Richi.
