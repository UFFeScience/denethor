# Synthetic Instance Files

Instâncias sintéticas do workflow usadas para modelagem e teste do escalonador. Todas seguem o formato descrito em [instance_file_format.md](instance_file_format.md).

Cada instância tem:
- **2 configurações de VM** (conf_id 1 e 2)
- **1 bucket** (`denethor_bucket`)
- **3 faixas de preço** de bucket (mesmo pricing do S3)
- Restrições: `max_running_time=100s`, `max_financial_cost=$0.10`

---

## Synthetic_7 — T3 D4 C2

**Arquivo:** `Synthetic_7_T3_D4_C2.txt`

### Topologia do DAG

```
d0 ──► t0 ──► d1 ──► t1 ──► d2
               │
               └────► t2 ──► d3
```

| Tarefa | Atividade | Tipo | CPU time | Entrada | Saída |
|---|---|---|---|---|---|
| t0 (id=10) | 1 | FX | 3.0s | d0 (id=90) | d1 (id=91) |
| t1 (id=11) | 1 | FX | 4.0s | d1 (id=91) | d2 (id=92) |
| t2 (id=12) | 2 | FX | 1.0s | d1 (id=91) | d3 (id=93) |

### Dados

| ID | Tamanho | Read avg | Write avg | Tipo |
|---|---|---|---|---|
| d0 (90) | 111 B | 2.0s | — | estático (entrada) |
| d1 (91) | 1033 B | 2.0s | 3.0s | dinâmico |
| d2 (92) | 1999 B | 3.0s | 1.0s | dinâmico |
| d3 (93) | 491 B | 2.0s | 2.0s | dinâmico |

### VMs disponíveis

| VM | Slowdown | Custo/s | Banda |
|---|---|---|---|
| 1 | 1.00 (base) | $0.0000051670/s | 1250 Mbps |
| 2 | 0.25 (4× mais rápida) | $0.0000826720/s | 5000 Mbps |

### Análise de custo mínimo

| Estratégia | Custo total |
|---|---|
| Melhor FX (conf_id=1) | $0.0000700000 |
| Melhor VM (VM=1) | $0.0001033400 |

---

## Synthetic_11 — T4 D7 C2

**Arquivo:** `Synthetic_11_T4_D7_C2.txt`

### Topologia do DAG

```
d0 ─┬──► t0 ──► d2 ─┐
    │                │
d1 ─┼──► t1 ──► d3 ─┼──► t3 ──► d6
    │                │
    └──► t2 ──► d4 ─┘
              └► d5 ─┘
```

| Tarefa | Atividade | Tipo | CPU time | Entrada | Saída |
|---|---|---|---|---|---|
| t0 (id=10) | 1 | FX | 7.0s | d0,d1 (90,91) | d2 (92) |
| t1 (id=11) | 1 | FX | 3.0s | d0,d1 (90,91) | d3 (93) |
| t2 (id=12) | 2 | FX | 9.0s | d1 (91) | d4,d5 (94,95) |
| t3 (id=13) | 2 | FX | 7.0s | d2,d3,d4,d5 (92,93,94,95) | d6 (96) |

### Dados

| ID | Tamanho | Read avg | Write avg | Tipo |
|---|---|---|---|---|
| d0 (90) | 1965 B | 4.0s | — | estático |
| d1 (91) | 564 B | 4.0s | — | estático |
| d2 (92) | 490 B | 1.0s | 1.0s | dinâmico |
| d3 (93) | 1703 B | 5.0s | 1.0s | dinâmico |
| d4 (94) | 527 B | 1.0s | 2.0s | dinâmico |
| d5 (95) | 1272 B | 5.0s | 2.0s | dinâmico |
| d6 (96) | 1130 B | 5.0s | 2.0s | dinâmico |

### VMs disponíveis

| VM | Slowdown | Custo/s | Banda |
|---|---|---|---|
| 1 | 1.00 (base) | $0.0000051670/s | 1250 Mbps |
| 3 | 0.25 (4× mais rápida) | $0.0000826720/s | 5000 Mbps |

### Análise de custo mínimo

| Estratégia | Custo total |
|---|---|
| Melhor FX (conf_id=1) | $0.0001250000 |
| Melhor VM (VM=1) | $0.0003513560 |

---

## Synthetic_12 — T5 D7 C2

**Arquivo:** `Synthetic_12_T5_D7_C2.txt`

### Topologia do DAG

```
d0 ──► t0 ──► d2 ──► t2 ──► d4
               │
d1 ──► t1 ──► d3 ──► t3 ──► d5
               │
               └────► t4 ──► d6
```

| Tarefa | Atividade | Tipo | CPU time | Entrada | Saída |
|---|---|---|---|---|---|
| t0 (id=10) | 1 | FX | 5.0s | d0 (90) | d2 (92) |
| t1 (id=11) | 1 | FX | 5.0s | d1 (91) | d3 (93) |
| t2 (id=12) | 2 | FX | 3.0s | d2 (92) | d4 (94) |
| t3 (id=13) | 2 | FX | 10.0s | d2,d3 (92,93) | d5 (95) |
| t4 (id=14) | 3 | FX | 8.0s | d3 (93) | d6 (96) |

### Dados

| ID | Tamanho | Read avg | Write avg | Tipo |
|---|---|---|---|---|
| d0 (90) | 1293 B | 2.0s | — | estático |
| d1 (91) | 626 B | 5.0s | — | estático |
| d2 (92) | 1037 B | 5.0s | 3.0s | dinâmico |
| d3 (93) | 236 B | 2.0s | 1.0s | dinâmico |
| d4 (94) | 818 B | 3.0s | 2.0s | dinâmico |
| d5 (95) | 1800 B | 3.0s | 2.0s | dinâmico |
| d6 (96) | 485 B | 2.0s | 1.0s | dinâmico |

### VMs disponíveis

| VM | Slowdown | Custo/s | Banda |
|---|---|---|---|
| 1 | 1.00 (base) | $0.0000051670/s | 1250 Mbps |
| 4 | 0.125 (8× mais rápida) | $0.0001653330/s | 5000 Mbps |

### Análise de custo mínimo

| Estratégia | Custo total |
|---|---|
| Melhor FX (conf_id=1) | $0.0001750000 |
| Melhor VM (VM=1) | $0.0003358550 |

---

## Synthetic_13 — T5 D8 C2

**Arquivo:** `Synthetic_13_T5_D8_C2.txt`

### Topologia do DAG

```
d0 ──► t0 ──► d1 ──► t1 ──► d2 ──► t2 ──► d4 ─┐
                      │                   └► d5 ─┤
                      └────► d3 ──► t3 ──► d6 ──┤
                                                  └──► t4 ──► d7
```

| Tarefa | Atividade | Tipo | CPU time | Entrada | Saída |
|---|---|---|---|---|---|
| t0 (id=10) | 1 | FX | 1.0s | d0 (90) | d1 (91) |
| t1 (id=11) | 1 | FX | 2.0s | d1 (91) | d2,d3 (92,93) |
| t2 (id=12) | 2 | FX | 6.0s | d2 (92) | d4,d5 (94,95) |
| t3 (id=13) | 2 | FX | 10.0s | d3 (93) | d6 (96) |
| t4 (id=14) | 3 | FX | 1.0s | d4,d5,d6 (94,95,96) | d7 (97) |

### Dados

| ID | Tamanho | Read avg | Write avg | Tipo |
|---|---|---|---|---|
| d0 (90) | 1590 B | 1.0s | — | estático |
| d1 (91) | 1502 B | 2.0s | 2.0s | dinâmico |
| d2 (92) | 1627 B | 4.0s | 1.0s | dinâmico |
| d3 (93) | 1963 B | 2.0s | 2.0s | dinâmico |
| d4 (94) | 668 B | 2.0s | 2.0s | dinâmico |
| d5 (95) | 597 B | 4.0s | 1.0s | dinâmico |
| d6 (96) | 614 B | 2.0s | 1.0s | dinâmico |
| d7 (97) | 1935 B | 2.0s | 3.0s | dinâmico |

### VMs disponíveis

| VM | Slowdown | Custo/s | Banda |
|---|---|---|---|
| 1 | 1.00 (base) | $0.0000051670/s | 1250 Mbps |
| 3 | 0.25 (4× mais rápida) | $0.0000826720/s | 5000 Mbps |

### Análise de custo mínimo

| Estratégia | Custo total |
|---|---|
| Melhor FX (conf_id=1) | $0.0001250000 |
| Melhor VM (VM=1) | $0.0000930060 |

> Única instância onde a estratégia VM é mais barata que FX.

---

## Synthetic_22 — T8 D14 C2

**Arquivo:** `Synthetic_22_T8_D14_C2.txt`

### Topologia do DAG

```
d0 ──► t0 ──► d2 ──► t1 ──► d3 ──► t4 ──► d7 ─┐
                                    ├──► d8  ├──► t7 ──► d13
d1 ──► t2 ──► d4 ──► t5 ──► d11 ──►┤    d9  │
  │                                 └──► d10 │
  └──► t3 ──► d5 ──► t6 ──► d12 ───────────►┤
        └──► d6 ──►(t6)                      │
                                   d11 ─────►┘
                                   d12 ─────►┘
```

| Tarefa | Atividade | Tipo | CPU time | Entrada | Saída |
|---|---|---|---|---|---|
| t0 (id=10) | 1 | FX | 9.0s | d0 (90) | d2 (92) |
| t1 (id=11) | 1 | FX | 10.0s | d2 (92) | d3 (93) |
| t2 (id=12) | 2 | FX | 4.0s | d1 (91) | d4 (94) |
| t3 (id=13) | 2 | FX | 4.0s | d1 (91) | d5,d6 (95,96) |
| t4 (id=14) | 3 | FX | 7.0s | d3 (93) | d7,d8,d9,d10 (97,98,99,910) |
| t5 (id=15) | 3 | FX | 3.0s | d4 (94) | d11 (911) |
| t6 (id=16) | 4 | FX | 6.0s | d5,d6 (95,96) | d12 (912) |
| t7 (id=17) | 4 | FX | 4.0s | d7,d8,d9,d10,d11,d12 (97–912) | d13 (913) |

### Dados

| ID | Tamanho | Read avg | Write avg | Tipo |
|---|---|---|---|---|
| d0 (90) | 1299 B | 4.0s | — | estático |
| d1 (91) | 1382 B | 1.0s | — | estático |
| d2 (92) | 1074 B | 5.0s | 2.0s | dinâmico |
| d3 (93) | 719 B | 1.0s | 3.0s | dinâmico |
| d4 (94) | 445 B | 1.0s | 1.0s | dinâmico |
| d5 (95) | 1667 B | 1.0s | 1.0s | dinâmico |
| d6 (96) | 1125 B | 2.0s | 2.0s | dinâmico |
| d7 (97) | 254 B | 1.0s | 3.0s | dinâmico |
| d8 (98) | 228 B | 2.0s | 3.0s | dinâmico |
| d9 (99) | 201 B | 4.0s | 3.0s | dinâmico |
| d10 (910) | 1584 B | 2.0s | 3.0s | dinâmico |
| d11 (911) | 271 B | 5.0s | 3.0s | dinâmico |
| d12 (912) | 201 B | 5.0s | 1.0s | dinâmico |
| d13 (913) | 440 B | 5.0s | 1.0s | dinâmico |

### VMs disponíveis

| VM | Slowdown | Custo/s | Banda |
|---|---|---|---|
| 1 | 1.00 (base) | $0.0000051670/s | 1250 Mbps |
| 2 | 0.50 (2× mais rápida) | $0.0000206670/s | 1250 Mbps |

> Única instância com 4 atividades distintas (1, 2, 3 e 4) e com **t7** como ponto de sincronização de 6 dados simultâneos.

---

## Comparativo geral

| Instância | Tasks | Dados | Atividades | Entradas estáticas | Ponto de sincronização (fan-in máximo) |
|---|---|---|---|---|---|
| Synthetic_7 | 3 | 4 | 2 | 1 | t1, t2 (1 entrada cada) |
| Synthetic_11 | 4 | 7 | 2 | 2 | t3 (4 entradas) |
| Synthetic_12 | 5 | 7 | 3 | 2 | t3 (2 entradas) |
| Synthetic_13 | 5 | 8 | 3 | 1 | t4 (3 entradas) |
| Synthetic_22 | 8 | 14 | 4 | 2 | t7 (6 entradas) |
