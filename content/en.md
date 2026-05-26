# Trevizo — Menu Content (English)

This file is the single source of truth for Trevizo menu copy in English.
The HTML preview is generated from this file by `build.py`.

**Format reference:**
- `# Menu: <name>` — one of five menus
- `## Side: <Front|Back>` — one of two sides
- `### <Section Name> {flag1, flag2}` — section, optional layout flags
- Items: `Name | Price | Description` (pipe-delimited)
- Quantity tags inline in name: `Birra Moretti Draught {400 ml}` (renders italic)
- Sub-items under a parent: lines starting with `~ ` use same pipe format
- `> Footer text` — section/page footer
- Lines starting with `// ` are comments, ignored by parser

**Cleanup applied vs. source `.docx`:**
- Brand spellings corrected (Moretti, Fischer, Johnnie Walker, Three Cents, Sartì, etc.)
- Italian/Greek accents restored (Viña, Espolòn, Patrón, Diplomático, etc.)
- Redundancies removed (`Red Vermouth Rosso` → `Vermouth Rosso`, `Aperol Spritz` as ingredient → `Aperol`)
- Beckett's standardized as the gin (pending bartender confirmation — see HANDOFF §8)
- Platter cold cuts items restored (Small 15 € / Large 25 €)
- Iced Tea flavors sub-block restored
- Ktima Mouson 9 grape list completed (added Assyrtiko)
- Negroni di Trevizo gin label normalized to match Aperitivo Negroni

---

# Menu: Wines

## Side: Front

### White
Viña Esmeralda | 7,50 / 32 € | Moscat · Gewürztraminer · Spain
Fontant Sauvignon Blanc | 6 / 24 € | Languedoc-Roussillon · France
Ktima Gerovassiliou | 8,50 / 36 € | Malagouzia · Epanomi · Thessaloniki
Ktima Biblia Chora | — / 42 € | Assyrtiko · Sauvignon Blanc · Kavala
Ktima Mouson 9 | — / 30 € | Trebbiano · Sauvignon Blanc · Assyrtiko · Voiotia

### Red {pad-right}
Fontant Merlot | 7 / 30 € | Languedoc-Roussillon · France
Lungarotti | — / 24 € | Sangiovese · Torgiano · Umbria · Italy
Gai'a Wines | — / 34 € | Agiorgitiko · Nemea PDO · Greece

> Continued overleaf

## Side: Back

### Rosé
Fontant Rosé | 6 / 24 € | Merlot · Languedoc-Roussillon · France
Viña Esmeralda Rosé | 7,50 / 32 € | Garnacha · Spain
Gaia Rosé 4-6 | 7,50 / 32 € | Agiorgitiko · Korinthia
Ktima Biblia Chora Rosé | — / 42 € | Syrah · Kavala · Greece
Pétale de Rose | — / 48 € | Grenache · Cinsault · Mourvèdre · Provence · France
Domaine Ott. By Ott. Rosé | — / 58 € | Grenache · Provence · France

### Champagne & Sparkling
Grande Vento Prosecco DOC | 7 / 34 € | Glera · Veneto · Italy
Truffle Hunter | 7 / 34 € | Moscato d'Asti · Langhe · Italy
Veuve Clicquot Yellow Brut | — / 210 € | Pinot Noir · Chardonnay · Meunier · France
Veuve Clicquot Rosé Brut | — / 240 € | Pinot Noir · Chardonnay · Meunier · France

> Vintage notes available on request

---

# Menu: Cocktails

## Side: Front

### Aperitivo Spritz
Aperol Spritz | 9 € | Aperol · Cinzano Prosecco · Soda Water
Campari Spritz | 9 € | Campari · Cinzano Prosecco · Soda Water
Americano | 10 € | Campari · Del Professore Vermouth Rosso · Soda Water
Negroni | 10 € | Beckett's London Dry Gin · Campari · Del Professore Vermouth Rosso
Crodino Spritz {non-alcoholic} | 8 € | Crodino 0% Alcohol · Soda Water

> Continued overleaf

## Side: Back {centered}

### Signature Spritz
Pink Spritz | 9 € | Lillet Rose Aperitif · Pink Grapefruit Soda
Velvet Highball | 10 € | Banana-Infused Whiskey · Tonka · Melon Soda
Fragola Spritz | 11 € | Cinzano Prosecco · Elderflower · Campari · Sartì Rosa · Strawberry Soda
Sole di Sicilia | 10 € | Aperol · Mandarin · Mango · Cinnamon · Soda Water
Limone Breeze | 11 € | Limoncello · Cinzano Prosecco · Cucumber · Ginger Beer
Negroni di Trevizo | 12 € | Beckett's London Dry Gin · Campari · Basil-Infused Vermouth Rosso · Shiitake

### Signature Cocktails
Mango Affair | 10 € | Beckett's London Dry Gin · Mango · Ginger · Lemon
Drama Queen | 10 € | Skyy Vodka · Passion Fruit · Salted Caramel · Citrus
Squeeze My Piña | 11 € | Espolòn Blanco · Pineapple · Spicy Agave · Lime
Bad Influence | 11 € | Wild Turkey 101 Bourbon · Hibiscus · Angostura Bitters · Orange · Lemon · Foam
Guilty Tai | 12 € | Kingston 62 Rum · Citrus · Almond · Orange Liqueur · Bitters · White Chocolate

> Nea Penteli · @trevizo.spritzeria

---

# Menu: Food

## Side: Front {centered}

### Wine Sides
Pomodorini & Mozzarella | 2,50 € | Stuffed Olives (2 pcs)
Baked Focaccia | 2,50 € | Rosemary · Sea Salt (4 pcs)

### Bruschetta
Pomodoro {6 pcs} | 9 € | Pesto · Burrata · Pomodorini
Parma {6 pcs} | 9 € | Prosciutto Parma · Pomodoro · Parmesan · Rocket · Truffle Oil

> Continued overleaf

## Side: Back

### Salads
Burrata | 9 € | Burrata · Pomodorini · Fresh Basil · Balsamic Cream
Il Giardino | 9 € | Mixed Leaves · Orange · Parmesan · Walnuts · Balsamic

### Pinsa Romana
Pomodoro & Burrata | 11 € | Salsa Pomodoro · Burrata · Pomodorini Tricolore · Fresh Basil
Prosciutto | 12 € | Salsa Pomodoro · Prosciutto Parma · Mozzarella · Rocket · Truffle Oil
Dante Inferno | 12 € | Salsa Pomodoro Piccante · Spianata Romana · Mozzarella
Tartufo | 14 € | Truffle Cream · Mozzarella · Porcini · Parmesan · Truffle Oil
Trevizo Pistachio | 14 € | Pomodoro · Mortadella · Mozzarella · Burrata · Pesto Pistachio · Fresh Pistachio

### Platter of Selected Cold Cuts
Small / Large | 15 € / 25 € |

### Desserts
Salami Tiramisu | 8 € | Mosaic Chocolate with Coffee Ganache
Italian Pistachio Cheesecake | 7 € | Cheesecake with Mascarpone & Pistachio
Dolce Tentazione | 8 € | Praline & Petit Beurre

> Nea Penteli · @trevizo.spritzeria

---

# Menu: Brunch

// Vermilion edge band with vertical text "SAT · SUN · 10:00—16:00" on both sides.
// Brunch service: Saturday & Sunday, 10:00–16:00 (operator-confirmed 2026-05-26).

## Side: Front {centered, edge-band}

### Italian Breads
Ciabatta Prosciutto | 9 € | Prosciutto Parma · Pesto · Mozzarella · Pomodoro · Rocket
Ciabatta Avo & Mozzarella | 8,50 € | Avocado · Pomodoro · Mozzarella · Olive Oil
Focaccia Milano | 9 € | Salami Milano · Truffle Cream · Pecorino Romano · Rocket

> Continued overleaf

## Side: Back {centered, edge-band}

### Salads
Burrata | 9 € | Burrata · Pomodorini · Fresh Basil · Balsamic Cream
Il Giardino | 9 € | Mixed Leaves · Orange · Parmesan · Walnuts · Balsamic

### Pinsa
Margherita | 10 € | Salsa Pomodoro · Mozzarella

### Platter of Selected Cold Cuts
Small / Large | 15 € / 25 € |

### Desserts
Salami Tiramisu | 8 € | Mosaic Chocolate with Coffee Ganache
Italian Pistachio Cheesecake | 7 € | Cheesecake with Mascarpone & Pistachio
Dolce Tentazione | 8 € | Praline & Petit Beurre

> Nea Penteli · @trevizo.spritzeria

---

# Menu: Beverages & Beer / Spirits

## Side: Front

### Coffee {col-2}
Espresso | 3 € |
Espresso Doppio | 3,50 € |
Cappuccino | 4,10 € |
Cappuccino Doppio | 4,40 € |
Latte | 4,50 € |
Iced Latte | 4,50 € |
Freddo Espresso | 4,10 € |
Freddo Cappuccino | 4,40 € |
Americano | 3,90 € |
Iced Americano | 3,90 € |
Hot Chocolate | 4,50 € |
Cold Chocolate | 4,50 € |

### Refreshments {col-2}
Coca-Cola | 4 € |
Coca-Cola Zero | 4 € |
Sprite | 4 € |
Three Cents Pink Grapefruit | 5 € |
Three Cents Aegean Tonic | 5 € |
Three Cents Ginger Beer | 5 € |
Three Cents Soda | 5 € |
Avra Sparkling {400 ml} | 4 € |
// HANDOFF §8 flag: source says 0,50 €; almost certainly a typo for 1,50 €. Confirm with operator.
Theoni {500 ml} | 0,50 € |
Avra Mineral {1 L} | 4 € |
Fresh Orange Juice | 4,40 € |
Fresh Mixed Juice | 5,50 € |
Iced Tea {Aristea 0% Sugar} | 5 € |
~ Shepherd's Tea | | Red Fruits · Peach · Tonka
~ White Tea | | Peach
~ Green Tea | | Lemongrass · Lemon
Trevizo Lemonade | 5 € |

### Beers {col-2}
Birra Moretti Draught {400 ml} | 5,50 € |
// HANDOFF §8 flag: keep "Mexico" qualifier? operator decision.
Sol {Mexico} | 5,50 € |
Nymfi | 4,50 € |
Fischer Lager | 5 € |
Heineken 0% | 5 € |
// Brand: Dathènes Beer (dathenesbeer.com).
Dathènes | 6 € |

> Spirits overleaf

## Side: Back

// LAYOUT NOTE: Left column = Gin + Rum + Tequila stacked.
// Right column = Vodka + Whiskey stacked. Whiskey is {pad-right} for mascot clearance.
// HANDOFF §8: 7 spirits below have no price in source. Operator decision pending — reinstate or omit.
// Currently OMITTED from V6: Beluga Noble, Elite by Stoli, G'Vine, El Dorado 12, Appleton Estate, Jose Cuervo La Familia, Balvenie 12 Triple Cask.

### Gin {column-left}
// HANDOFF §8 flag: source spells "Bicken's / Bickens / Bickers" — standardized to Beckett's. Confirm with bartender.
Beckett's London Dry | 9 € |
Tanqueray London Dry | 10 € |
Tanqueray N°10 | 14 € |
Tanqueray 0% | 10 € |
Bulldog Gin | 10 € |
Hendrick's | 14 € |
Monkey 47 | 14 € |
Gin Mare | 14 € |

### Rum {column-left}
Kingston 62 White | 9 € |
Kingston 62 Jamaican | 9 € |
Havana Club 3 Años | 9 € |
Havana Club 7 | 12 € |
Diplomático Mantuano | 13 € |
Diplomático Reserva Exclusiva | 22 € |
Zacapa 23 | 14 € |

### Tequila {column-left}
Espolòn Blanco | 11 € |
Espolòn Reposado | 12 € |
Patrón Blanco | 15 € |
Patrón Reposado | 16 € |
Patrón Añejo | 20 € |
Don Julio Blanco | 15 € |
Don Julio Reposado | 17 € |
Don Julio Añejo | 20 € |
Don Julio 1942 | 60 € |

### Vodka {column-right}
Skyy Vodka | 9 € |
Russian Standard | 9 € |
Tito's | 12 € |
Belvedere | 14 € |
Cîroc | 14 € |

### Whiskey {column-right}
Jameson | 9 € |
Jameson Black Barrel | 13 € |
Johnnie Walker Red | 9 € |
Johnnie Walker Black | 14 € |
Johnnie Walker Gold | 16 € |
Wild Turkey 101 Bourbon | 12 € |
Jack Daniel's N°7 | 12 € |
Talisker 10 Y.O. | 16 € |
Lagavulin 12 Y.O. | 20 € |

> Nea Penteli · Plateia Iroon Politechniou 43 · @trevizo.spritzeria
