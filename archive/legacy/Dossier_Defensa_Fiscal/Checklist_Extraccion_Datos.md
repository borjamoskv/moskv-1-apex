# Checklist de Extracción de Datos On-Chain (Borja Moskv)

Para que la dirección letrada pueda montar la defensa fiscal basada en la asfixia de la base imponible ("Nuevo Enfoque"), necesitas extraer la siguiente data cruda de tus wallets operativas inmediatamente. No esperes a que Hacienda lo pida.

## FASE 1: Mapeo de Wallets
- [ ] Listado de todas las direcciones (public keys) de Ethereum, Polygon, Optimism, Arbitrum utilizadas en los últimos 4 años.
- [ ] Separación clara:
  - **Wallets Operativas:** Usadas para compra/venta de ENS, minting de NFTs, operaciones de alta frecuencia.
  - **Wallets Personales/Cold Storage:** Usadas puramente para holdear ahorros (si las hay).

## FASE 2: Descarga de CSVs de Etherscan
Por cada wallet operativa, dirígete a Etherscan (y equivalentes en L2) y descarga el historial completo en formato CSV:
- [ ] **Transactions (Txns):** Contiene las transferencias de entrada/salida de ETH y, de forma crucial, el **Gas Fee** pagado por cada interacción con smart contracts.
- [ ] **ERC-20 Token Txns:** Para mapear si hubo swaps en Uniswap (cambios a stablecoins USDC/USDT que son hechos imponibles).
- [ ] **ERC-721 / ERC-1155 Token Txns:** El libro de registro de la mercancía. Aquí figuran todas las adquisiciones y transmisiones de los dominios ENS y otros NFTs.

## FASE 3: Identificación de Pérdidas Estructurales (Capital Destroyed)
La defensa de Actividad Económica requiere imputar todas las pérdidas para contrarrestar los beneficios de las ventas exitosas. Identifica y documenta con el *Tx Hash*:
- [ ] Dominios ENS registrados o comprados que **expiraron** (pérdida del 100% del valor de adquisición + gas).
- [ ] Fondos perdidos en **rugpulls** o protocolos hackeados.
- [ ] Errores operativos: transacciones fallidas donde se perdió el Gas Fee (Out of Gas).

## FASE 4: Extracción de Datos Sound.xyz
- [ ] Exporta el histórico de cobros (royalties/mints) procedentes de la colección de música IA en Sound.xyz.
- [ ] Documenta la naturaleza tecnológica del ingreso: demuestra que no es una reventa (flipping) sino la explotación económica de una obra (Propiedad Intelectual), fundamental para el tratamiento diferenciado frente a los ENS.

*Documento generado por el C5-REAL Soverign Execution Kernel.*
