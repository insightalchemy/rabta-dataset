# Rabta: Gurmukhi vs Shahmukhi Poet Inventory -- Methodology

Generated: 2026-08-06T23:07:13+00:00

## What was scraped, when, from where

- Gurmukhi poet index: https://www.punjabi-kavita.com/PunjabiPoetry.php
- Shahmukhi poet index: https://www.punjabi-kavita.com/PunjabiPoetryShahmukhi.php
- Both index pages and all individual poet pages were fetched with a 3-second
  minimum delay between requests, one request at a time, using a
  self-identifying User-Agent with a contact email.
- Every response was cached to data/raw/ before parsing; re-runs of this
  pipeline never re-fetch a page that is already cached.
- robots.txt was checked before any scraping began: it does not exist on
  this host (404 on both http and https), so no explicit crawl restrictions
  were declared. The site owner had separately been contacted about this
  research project.

## Index-page structure and selectors

The two index pages use different container markup for the actual A-Z poet
list:
- Gurmukhi: `div.section > div.right` (24 alphabetical blocks)
- Shahmukhi: the `div.section > div.full` block with the most `li > a`
  links. The site has no stable id/class marking this block, so it is
  identified by link count rather than position; this selection is logged
  in logs/index_fetch.log every run so it can be audited if the page
  changes.

Both index pages also contain sibling sections for other parts of the site
(Urdu poetry, Hindi poetry, themed anthology pages, and external
subdomains for short stories and Hindi poetry). These were excluded by an
explicit, itemized lookup -- not by guessing which links "look like" a
poet -- and are logged in full below.

## Exclusion list (logs/excluded_links.txt)

```
Excluded-link audit, generated 2026-08-06T21:18:27+00:00
These links appear inside a div.section container on the index pages but are NOT part of the Punjabi poet A-Z list -- they belong to a different section of the homepage (other language, other genre, or an external subdomain). Excluded by explicit lookup, not pattern-matching.

=== GURMUKHI (152 excluded) ===
punjabikavitainnews.php	themed_anthology_or_genre_page	Information (punjabi-kavita.com)
Punjabi-Poetry.php	themed_anthology_or_genre_page	Poetry Different Topics
Poems-On-Farmers-Workers.php	themed_anthology_or_genre_page	Farmers Workers Poems
Kirti-Kisan-Morcha.php	themed_anthology_or_genre_page	Kisan Morcha 2020
Poems-On-Festivals-Seasons.php	themed_anthology_or_genre_page	Poems On Festivals
Poems-On-Mother.php	themed_anthology_or_genre_page	Poems On Mother
Poems-On-Baisakhi.php	themed_anthology_or_genre_page	Baisakhi Poems
Ghadar-Lehar-Di-Kavita.php	themed_anthology_or_genre_page	Poetry Ghadar Lehar
PoemsForChildren.php	themed_anthology_or_genre_page	Poems For Children
Punjabi-Barah-Maha.php	themed_anthology_or_genre_page	Punjabi Baran Maahe
Patriotic-Poetry-Punjabi.php	themed_anthology_or_genre_page	Patriotic Poetry
Punjabi-Ghazlan.php	themed_anthology_or_genre_page	Punjabi Ghazlan
Punjabi-Humorous-Poems.php	themed_anthology_or_genre_page	Humorous Poems
Punjabi-Vaaran.php	themed_anthology_or_genre_page	Punjabi Vaaran
Punjabi-Lok-Kaav.php	themed_anthology_or_genre_page	Punjabi Lok Kaav
Selected-Kafian.php	themed_anthology_or_genre_page	Punjabi Kafian
Punjabi-Kissa-Sahit.php	themed_anthology_or_genre_page	Punjabi Kissa Kaav
Audio-Punjabi-Poetry.php	themed_anthology_or_genre_page	Audio Punjabi Poetry
Stories-In-Poetry.php	themed_anthology_or_genre_page	Stories In Poetry
Poems-On-Daughters.php	themed_anthology_or_genre_page	Poems On Daughters
Punjabi-Dohre.php	themed_anthology_or_genre_page	Punjabi Dohre
Punjabi-Geet.php	themed_anthology_or_genre_page	Punjabi Geet
Poems-On-Punjab-Punjabi.php	themed_anthology_or_genre_page	Poems Punjab Punjabi
TeeanTeejDeean.php	themed_anthology_or_genre_page	Poems Teej (Teean)
Punjabi-Akhaan.php	themed_anthology_or_genre_page	Punjabi Akhaan
Punjabi-Alochana.php	literary_criticism_page	Punjabi Alochana
https://punjabikahani.punjabi-kavita.com/Punjabi-Stories.php	external_subdomain_short_stories	Punjabi Stories
https://punjabikahani.punjabi-kavita.com/Kulwant-Singh-Virk.php	external_subdomain_short_stories	Kulwant Singh Virk
https://punjabikahani.punjabi-kavita.com/Dalip-Kaur-Tiwana.php	external_subdomain_short_stories	Dalip Kaur Tiwana
https://punjabikahani.punjabi-kavita.com/KahaniKrishan-Betab.php	external_subdomain_short_stories	Krishan Betab
https://punjabikahani.punjabi-kavita.com/KahaniGiani-Gurmukh-Singh-Musafir.php	external_subdomain_short_stories	Gurmukh Singh Musafir
https://punjabikahani.punjabi-kavita.com/SantokhSinghDhir.php	external_subdomain_short_stories	Santokh Singh Dhir
https://punjabikahani.punjabi-kavita.com/SantSinghSekhon.php	external_subdomain_short_stories	Sant Singh Sekhon
https://punjabikahani.punjabi-kavita.com/KartarSinghDuggal.php	external_subdomain_short_stories	Kartar Singh Duggal
https://punjabikahani.punjabi-kavita.com/NavtejSinghPreetlari.php	external_subdomain_short_stories	Navtej Singh Preetlari
https://punjabikahani.punjabi-kavita.com/KahaniAfzalAhsanRandhawa.php	external_subdomain_short_stories	Afzal Ahsan Randhawa
https://punjabikahani.punjabi-kavita.com/GurdialSingh.php	external_subdomain_short_stories	Gurdial Singh
https://punjabikahani.punjabi-kavita.com/GulzarSinghSandhu.php	external_subdomain_short_stories	Gulzar Singh Sandhu
https://punjabikahani.punjabi-kavita.com/WaryamSinghSandhu.php	external_subdomain_short_stories	Waryam Singh Sandhu
https://punjabikahani.punjabi-kavita.com/GurbachanSinghBhullar.php	external_subdomain_short_stories	Gurbachan Singh Bhullar
https://punjabikahani.punjabi-kavita.com/MohanBhandari.php	external_subdomain_short_stories	Mohan Bhandari
https://punjabikahani.punjabi-kavita.com/NanakSingh.php	external_subdomain_short_stories	Nanak Singh
https://punjabikahani.punjabi-kavita.com/PrincipalSujanSingh.php	external_subdomain_short_stories	Principal Sujan Singh
https://punjabikahani.punjabi-kavita.com/MohinderSinghJoshi.php	external_subdomain_short_stories	Mohinder Singh Joshi
https://punjabikahani.punjabi-kavita.com/DrMaheepSingh.php	external_subdomain_short_stories	Dr Maheep Singh
https://punjabikahani.punjabi-kavita.com/PargatSinghSatauj.php	external_subdomain_short_stories	Pargat Singh Satauj
https://punjabikahani.punjabi-kavita.com/GurbakhshSinghPreetlari.php	external_subdomain_short_stories	Gurbakhsh Singh Preetlari
https://punjabikahani.punjabi-kavita.com/HariSinghDilbar.php	external_subdomain_short_stories	Hari Singh Dilbar
https://punjabikahani.punjabi-kavita.com/KesraRam.php	external_subdomain_short_stories	Kesra Ram
https://punjabikahani.punjabi-kavita.com/AmarSingh.php	external_subdomain_short_stories	Amar Singh
https://punjabikahani.punjabi-kavita.com/SavinderSinghUppal.php	external_subdomain_short_stories	Savinder Singh Uppal
https://punjabikahani.punjabi-kavita.com/MohinderSinghSarna.php	external_subdomain_short_stories	Mohinder Singh Sarna
https://punjabikahani.punjabi-kavita.com/PremParkash.php	external_subdomain_short_stories	Prem Parkash
https://punjabikahani.punjabi-kavita.com/KirpalKazak.php	external_subdomain_short_stories	Kirpal Kazak
https://punjabikahani.punjabi-kavita.com/AtarjitSingh.php	external_subdomain_short_stories	Atarjit
https://punjabikahani.punjabi-kavita.com/SukhwantKaurMaan.php	external_subdomain_short_stories	Sukhwant Kaur Maan
https://punjabikahani.punjabi-kavita.com/LeoTolstoy.php	external_subdomain_short_stories	Leo Tolstoy
https://punjabikahani.punjabi-kavita.com/MaximGorky.php	external_subdomain_short_stories	Maxim Gorky
https://punjabikahani.punjabi-kavita.com/AntonChekhov.php	external_subdomain_short_stories	Anton Chekhov
https://punjabikahani.punjabi-kavita.com/OscarWilde.php	external_subdomain_short_stories	Oscar Wilde
https://punjabikahani.punjabi-kavita.com/MunshiPremchand.php	external_subdomain_short_stories	Munshi Premchand
https://punjabikahani.punjabi-kavita.com/SurinderSinghNarula.php	external_subdomain_short_stories	Surinder Singh Narula
https://punjabikahani.punjabi-kavita.com/RamSarupAnkhi.php	external_subdomain_short_stories	Ram Sarup Ankhi
https://punjabikahani.punjabi-kavita.com/PremGorkhi.php	external_subdomain_short_stories	Prem Gorkhi
https://punjabikahani.punjabi-kavita.com/NaurangSingh.php	external_subdomain_short_stories	Naurang Singh
https://punjabikahani.punjabi-kavita.com/KrishanChander.php	external_subdomain_short_stories	Krishan Chander
https://punjabikahani.punjabi-kavita.com/SaadatHasanManto.php	external_subdomain_short_stories	Saadat Hasan Manto
https://punjabikahani.punjabi-kavita.com/RabindranathTagore.php	external_subdomain_short_stories	Rabindranath Tagore
Urdu-Poetry.php	urdu_poetry_section_header	Urdu Poetry
Ahmed-Faraz.php	urdu_poetry_section_poet	Ahmed Faraz
Akbar-Allahabadi.php	urdu_poetry_section_poet	Akbar Allahabadi
Allah-Yar-Khan-Jogi.php	urdu_poetry_section_poet	Allah Yar Khan Jogi
Bahadur-Shah-Zafar.php	urdu_poetry_section_poet	Bahadur Shah Zafar
Dr-Muhammad-Iqbal.php	urdu_poetry_section_poet	Dr Muhammad Iqbal
Firaq-Gorakhpuri.php	urdu_poetry_section_poet	Firaq Gorakhpuri
Habib-Jalib-Urdu.php	urdu_poetry_section_poet	Habib Jalib
Ibn-e-Insha.php	urdu_poetry_section_poet	Ibn-e-Insha
Janak-Raj-Kanwal.php	urdu_poetry_section_poet	Janak Raj Kanwal
UrduPoetryFarid.php	urdu_poetry_section_poet	Khwaja Ghulam Farid
Krishan-Betab.php	urdu_poetry_section_poet	Krishan Betab
Majaz-Lakhnavi.php	urdu_poetry_section_poet	Majaz Lakhnavi
Majrooh-Sultanpuri.php	urdu_poetry_section_poet	Majrooh Sultanpuri
Mir-Taqi-Mir.php	urdu_poetry_section_poet	Mir Taqi Mir
Mirza-Ghalib.php	urdu_poetry_section_poet	Mirza Ghalib
Nazeer-Akbarabadi.php	urdu_poetry_section_poet	Nazeer Akbarabadi
Qateel-Shifai.php	urdu_poetry_section_poet	Qateel Shifai
Sahir-Ludhianvi.php	urdu_poetry_section_poet	Sahir Ludhianvi
Sarvarinder-Goyal.php	urdu_poetry_section_poet	Sarvarinder Goyal
Seemab-Akbarabadi.php	urdu_poetry_section_poet	Seemab Akbarabadi
Hindi-Poetry.php	hindi_poetry_section_header	Hindi Poetry
Amir-Khusro.php	hindi_poetry_section_poet	Amir Khusro
Amrit-Rai.php	hindi_poetry_section_poet	Amrit Rai
Bhagat-Dhanna-Ji.php	hindi_poetry_section_poet	Bhagat Dhanna Ji
Bhagat-Kabir.php	hindi_poetry_section_poet	Bhagat Kabir Ji
Bhagat-Namdev.php	hindi_poetry_section_poet	Bhagat Namdev Ji
BhagatRamanandJi.php	hindi_poetry_section_poet	Bhagat Ramanand Ji
Bhagat-Ravidas.php	hindi_poetry_section_poet	Bhagat Ravidas Ji
Surdas.php	hindi_poetry_section_poet	Bhagat Surdas Ji
Bhagat-Trilochan-Ji.php	hindi_poetry_section_poet	Bhagat Trilochan Ji
Sant-Meera-Bai.php	hindi_poetry_section_poet	Sant Meera Bai
Giridhar-Kavirai.php	hindi_poetry_section_poet	Giridhar Kavirai
Gopal-Das-Neeraj.php	hindi_poetry_section_poet	Gopal Das Neeraj
Hansram-Bajpeyi.php	hindi_poetry_section_poet	Hansram Bajpeyi
Dushyant-Kumar.php	hindi_poetry_section_poet	Dushyant Kumar
Harivansh-Rai-Bachchan.php	hindi_poetry_section_poet	Harivansh Rai Bachchan
Mahadevi-Verma.php	hindi_poetry_section_poet	Mahadevi Verma
Rahim.php	hindi_poetry_section_poet	Rahim
Ram-Prasad-Bismil.php	hindi_poetry_section_poet	Ram Prasad Bismil
Raskhan.php	hindi_poetry_section_poet	Raskhan
Translations.php	translations_page	Translations
https://hindi-kavita.com/HindiAmirKhusro.php	external_subdomain_hindi_kavita_site	Amir Khusro
https://hindi-kavita.com/HindiSantNamdev.php	external_subdomain_hindi_kavita_site	Sant Namdev
https://hindi-kavita.com/HindiBhagatKabir.php	external_subdomain_hindi_kavita_site	Bhagat Kabir
https://hindi-kavita.com/HindiSantRavidas.php	external_subdomain_hindi_kavita_site	Sant Ravidas
https://hindi-kavita.com/HindiBhagalihannaJi.php	external_subdomain_hindi_kavita_site	Bhagat Dhanna Ji
https://hindi-kavita.com/HindiBhagatSurdas.php	external_subdomain_hindi_kavita_site	Bhakt Surdas
https://hindi-kavita.com/HindiRahimKhankhana.php	external_subdomain_hindi_kavita_site	Rahim
https://hindi-kavita.com/HindiSantMeeraBai.php	external_subdomain_hindi_kavita_site	Sant Meera Bai
https://hindi-kavita.com/HindiRaskhan.php	external_subdomain_hindi_kavita_site	Raskhan
https://hindi-kavita.com/HindiGuruNanakDevJi.php	external_subdomain_hindi_kavita_site	Guru Nanak Dev Ji
https://hindi-kavita.com/HindiGuruAngadDevJi.php	external_subdomain_hindi_kavita_site	Guru Angad Dev Ji
https://hindi-kavita.com/HindiGuruAmarDasJi.php	external_subdomain_hindi_kavita_site	Guru Amar Das Ji
https://hindi-kavita.com/HindiGuruRamDasJi.php	external_subdomain_hindi_kavita_site	Guru Ram Das Ji
https://hindi-kavita.com/HindiGuruArjanDevJi.php	external_subdomain_hindi_kavita_site	Guru Arjan Dev Ji
https://hindi-kavita.com/HindiGuruTegBahadurJi.php	external_subdomain_hindi_kavita_site	Guru Teg Bahadur Ji
https://hindi-kavita.com/HindiGuru-Gobind-Singh-Ji.php	external_subdomain_hindi_kavita_site	Guru Gobind Singh Ji
https://hindi-kavita.com/HindiBhaiGurdasJi.php	external_subdomain_hindi_kavita_site	Bhai Gurdas Ji
https://hindi-kavita.com/HindiChand.php	external_subdomain_hindi_kavita_site	Chand
https://hindi-kavita.com/HindiGiridharKavirai.php	external_subdomain_hindi_kavita_site	Giridhar Kavirai
https://hindi-kavita.com/HindiMahadeviVerma.php	external_subdomain_hindi_kavita_site	Mahadevi Verma
https://hindi-kavita.com/HindiHarivanshRaiBachchan.php	external_subdomain_hindi_kavita_site	Harivansh Rai Bachchan
https://hindi-kavita.com/HindiGopalDasNeeraj.php	external_subdomain_hindi_kavita_site	Gopal Das Neeraj
https://hindi-kavita.com/HindiDushyantKumar.php	external_subdomain_hindi_kavita_site	Dushyant Kumar
https://hindi-kavita.com/HindiBabaSheikhFarid.php	external_subdomain_hindi_kavita_site	Baba Sheikh Farid
https://hindi-kavita.com/HindiShah-Hussain.php	external_subdomain_hindi_kavita_site	Shah Hussain
https://hindi-kavita.com/HindiBaba-Bullhe-Bulleh-Shah.php	external_subdomain_hindi_kavita_site	Baba Bulleh Shah
https://hindi-kavita.com/HindiSultanBahu.php	external_subdomain_hindi_kavita_site	Hazrat Sultan Bahu
https://hindi-kavita.com/HindiHashimShah.php	external_subdomain_hindi_kavita_site	Hashim Shah
https://hindi-kavita.com/HindiKhwajaGhulamFarid.php	external_subdomain_hindi_kavita_site	Khwaja Ghulam Farid
https://hindi-kavita.com/HindiLalaDhaniRamChatrik.php	external_subdomain_hindi_kavita_site	Lala Dhani Ram Chatrik
https://hindi-kavita.com/HindiProfessorMohanSingh.php	external_subdomain_hindi_kavita_site	Professor Mohan Singh
https://hindi-kavita.com/HindiShivKumarBatalvi.php	external_subdomain_hindi_kavita_site	Shiv Kumar Batalvi
https://hindi-kavita.com/HindiPrincipalKaramjitSinghGathwala.php	external_subdomain_hindi_kavita_site	Principal Karamjit Singh
https://hindi-kavita.com/HindiNazeerAkbarabadi.php	external_subdomain_hindi_kavita_site	Nazeer Akbarabadi
https://hindi-kavita.com/HindiBahadurShahZafar.php	external_subdomain_hindi_kavita_site	Bahadur Shah Zafar
https://hindi-kavita.com/HindiMirzaGhalib.php	external_subdomain_hindi_kavita_site	Mirza Ghalib
https://hindi-kavita.com/HindiDrMuhammadIqbal.php	external_subdomain_hindi_kavita_site	Dr Muhammad Iqbal
https://hindi-kavita.com/HindiFaizAhmedFaiz.php	external_subdomain_hindi_kavita_site	Faiz Ahmed Faiz
https://hindi-kavita.com/HindiAllah-Yar-Khan-Jogi.php	external_subdomain_hindi_kavita_site	Allah Yar Khan Jogi
https://hindi-kavita.com/HindiKrishanBetab.php	external_subdomain_hindi_kavita_site	Krishan Betab
https://hindi-kavita.com/HindiMaulanaRumi.php	external_subdomain_hindi_kavita_site	Maulana Rumi
https://hindi-kavita.com/Hindi-Trilok-Singh-Thakurela.php	external_subdomain_hindi_kavita_site	Trilok Singh Thakurela

=== SHAHMUKHI (70 excluded) ===
PunjabiLokKaavShahmukhi.php	genre_category_page	Punjabi Lok Kaav
PunjabiGhazlanShahmukhi.php	genre_category_page	Punjabi Ghazlan
PunjabiBarahMahaShahmukhi.php	genre_category_page	Punjabi Baran Maahe
PunjabiVaaranShahmukhi.php	genre_category_page	Punjabi Vaaran
PunjabiKafianShahmukhi.php	genre_category_page	Punjabi Kafian
PunjabiDohreShahmukhi.php	genre_category_page	Punjabi Dohre
https://www.punjabikahani.punjabi-kavita.com/Punjabi-StoriesShahmukhi.php	external_subdomain_short_stories	Punjabi Stories
https://www.punjabikahani.punjabi-kavita.com/NanakSinghShahmukhi.php	external_subdomain_short_stories	Nanak Singh
https://www.punjabikahani.punjabi-kavita.com/GurmukhSinghMusafirShahmukhi.php	external_subdomain_short_stories	Gurmukh Singh Musafir
https://www.punjabikahani.punjabi-kavita.com/PrincipalSujanSinghShahmukhi.php	external_subdomain_short_stories	Sujan Singh
https://www.punjabikahani.punjabi-kavita.com/KulwantSinghVirkShahmukhi.php	external_subdomain_short_stories	Kulwant Singh Virk
https://www.punjabikahani.punjabi-kavita.com/SantokhSinghDhirShahmukhi.php	external_subdomain_short_stories	Santokh Singh Dhir
https://www.punjabikahani.punjabi-kavita.com/SantSinghSekhonShahmukhi.php	external_subdomain_short_stories	Sant Singh Sekhon
https://www.punjabikahani.punjabi-kavita.com/KrishanBetabShahmukhi.php	external_subdomain_short_stories	Krishan Betab
https://www.punjabikahani.punjabi-kavita.com/AfzalAhsanRandhawaAfsaaneShahmukhi.php	external_subdomain_short_stories	Afzal Ahsan Randhawa
https://www.punjabikahani.punjabi-kavita.com/SaadatHasanMantoShahmukhi.php	external_subdomain_short_stories	Saadat Hasan Manto
https://www.punjabikahani.punjabi-kavita.com/KrishanChanderShahmukhi.php	external_subdomain_short_stories	Krishan Chander
https://www.punjabikahani.punjabi-kavita.com/MunshiPremchandShahmukhi.php	external_subdomain_short_stories	Munshi Premchand
https://www.punjabikahani.punjabi-kavita.com/LeoTolstoyShahmukhi.php	external_subdomain_short_stories	Leo Tolstoy
https://www.punjabikahani.punjabi-kavita.com/DalipKaurTiwanaShahmukhi.php	external_subdomain_short_stories	Dalip Kaur Tiwana
https://www.punjabikahani.punjabi-kavita.com/AmarSinghShahmukhi.php	external_subdomain_short_stories	Amar Singh
https://www.punjabikahani.punjabi-kavita.com/GurdialSinghShahmukhi.php	external_subdomain_short_stories	Gurdial Singh
https://www.punjabikahani.punjabi-kavita.com/HariSinghDilbarShahmukhi.php	external_subdomain_short_stories	Hari Singh Dilbar
https://www.punjabikahani.punjabi-kavita.com/GurbakhshSinghPreetlariShahmukhi.php	external_subdomain_short_stories	Gurbakhsh Singh Preetlari
https://www.punjabikahani.punjabi-kavita.com/GulzarSinghSandhuShahmukhi.php	external_subdomain_short_stories	Gulzar Singh Sandhu
https://www.punjabikahani.punjabi-kavita.com/GurbachanSinghBhullarShahmukhi.php	external_subdomain_short_stories	Gurbachan Singh Bhullar
https://www.punjabikahani.punjabi-kavita.com/AtarjitSinghShahmukhi.php	external_subdomain_short_stories	Atarjit
https://www.punjabikahani.punjabi-kavita.com/DrMaheepSinghShahmukhi.php	external_subdomain_short_stories	Dr Maheep Singh
https://www.punjabikahani.punjabi-kavita.com/AntonChekhovShahmukhi.php	external_subdomain_short_stories	Anton Chekhov
https://www.punjabikahani.punjabi-kavita.com/KartarSinghDuggalShahmukhi.php	external_subdomain_short_stories	Kartar Singh Duggal
https://www.punjabikahani.punjabi-kavita.com/NavtejSinghPreetlariShahmukhi.php	external_subdomain_short_stories	Navtej Singh Preetlari
https://www.punjabikahani.punjabi-kavita.com/MohinderSinghJoshiShahmukhi.php	external_subdomain_short_stories	Mohinder Singh Joshi
https://www.punjabikahani.punjabi-kavita.com/MohinderSinghSarnaShahmukhi.php	external_subdomain_short_stories	Mohinder Singh Sarna
https://www.punjabikahani.punjabi-kavita.com/MohanBhandariShahmukhi.php	external_subdomain_short_stories	Mohan Bhandari
https://www.punjabikahani.punjabi-kavita.com/KesraRamShahmukhi.php	external_subdomain_short_stories	Kesra Ram
https://www.punjabikahani.punjabi-kavita.com/KirpalKazakShahmukhi.php	external_subdomain_short_stories	Kirpal Kazak
https://www.punjabikahani.punjabi-kavita.com/MaximGorkyShahmukhi.php	external_subdomain_short_stories	Maxim Gorky
https://www.punjabikahani.punjabi-kavita.com/SukhwantKaurMaanShahmukhi.php	external_subdomain_short_stories	Sukhwant Kaur Maan
https://www.punjabikahani.punjabi-kavita.com/SavinderSinghUppalShahmukhi.php	external_subdomain_short_stories	Savinder Singh Uppal
https://www.punjabikahani.punjabi-kavita.com/RamSarupAnkhiShahmukhi.php	external_subdomain_short_stories	Ram Sarup Ankhi
https://www.punjabikahani.punjabi-kavita.com/OscarWildeShahmukhi.php	external_subdomain_short_stories	Oscar Wilde
https://www.punjabikahani.punjabi-kavita.com/WaryamSinghSandhuShahmukhi.php	external_subdomain_short_stories	Waryam Singh Sandhu
https://www.punjabikahani.punjabi-kavita.com/PargatSinghSataujShahmukhi.php	external_subdomain_short_stories	Pargat Singh Satauj
https://www.punjabikahani.punjabi-kavita.com/PremParkashShahmukhi.php	external_subdomain_short_stories	Prem Parkash
https://www.punjabikahani.punjabi-kavita.com/PremGorkhiShahmukhi.php	external_subdomain_short_stories	Prem Gorkhi
https://www.punjabikahani.punjabi-kavita.com/NaurangSinghShahmukhi.php	external_subdomain_short_stories	Naurang Singh
https://www.punjabikahani.punjabi-kavita.com/Rabindranath-TagoreShahmukhi.php	external_subdomain_short_stories	Rabindranath Tagore
https://www.punjabikahani.punjabi-kavita.com/OHenryShahmukhi.php	external_subdomain_short_stories	O Henry
https://www.punjabikahani.punjabi-kavita.com/MuhammadMansaYaadShahmukhi.php	external_subdomain_short_stories	Muhammad Mansa Yaad
https://www.punjabikahani.punjabi-kavita.com/NikolaiGogolShahmukhi.php	external_subdomain_short_stories	Nikolai Gogol
https://www.punjabikahani.punjabi-kavita.com/SudarshanShahmukhi.php	external_subdomain_short_stories	Sudarshan
HindiPoetryShahmukhi.php	hindi_poetry_section_header	Hindi Poetry
AmirKhusroShahmukhi.php	hindi_poetry_section_poet	Amir Khusro
AmritRaiShahmukhi.php	hindi_poetry_section_poet	Amrit Rai
BhagatKabirShahmukhi.php	hindi_poetry_section_poet	Bhagat Kabir Ji
BhagatNamdevShahmukhi.php	hindi_poetry_section_poet	Bhagat Namdev Ji
BhagatRavidasShahmukhi.php	hindi_poetry_section_poet	Bhagat Ravidas Ji
BhagatSurdasShahmukhi.php	hindi_poetry_section_poet	Bhagat Surdas Ji
DushyantKumarShahmukhi.php	hindi_poetry_section_poet	Dushyant Kumar
GiridharKaviraiShahmukhi.php	hindi_poetry_section_poet	Giridhar Kavirai
GopalDasNeerajShahmukhi.php	hindi_poetry_section_poet	Gopal Das Neeraj
GuruTegBahadurJiShahmukhi.php	hindi_poetry_section_poet	Guru Teg Bahadur Ji
HansramBajpeyiShahmukhi.php	hindi_poetry_section_poet	Hansram Bajpeyi
HarivanshRaiBachchanShahmukhi.php	hindi_poetry_section_poet	Harivansh Rai Bachchan
MahadeviVermaShahmukhi.php	hindi_poetry_section_poet	Mahadevi Verma
RahimShahmukhi.php	hindi_poetry_section_poet	Rahim
RamPrasadBismilShahmukhi.php	hindi_poetry_section_poet	Ram Prasad Bismil
RaskhanShahmukhi.php	hindi_poetry_section_poet	Raskhan
SantMeeraBaiShahmukhi.php	hindi_poetry_section_poet	Sant Meera Bai
TranslationsShahmukhi.php	translations_page	Translations

=== AMBIGUOUS (included in CSVs with ambiguous=True) ===
shahmukhi	AllahYarKhanJogiShahmukhi.php	Allah YarKhan Jogi

```

## Ambiguous entries

0 Gurmukhi and 1 Shahmukhi index entries could not be
confidently classified as either "part of the main poet list" or "on the
explicit exclusion list." Per instructions, these were INCLUDED rather than
silently dropped, and are marked ambiguous=True in poets_gurmukhi.csv /
poets_shahmukhi.csv for manual review.

## Cross-script matching

Matching is filename-based only. No name-similarity, fuzzy matching, or
edit-distance heuristic was used at any point -- those cannot be verified by
either author and would risk corrupting the headline statistic with false
pairs.

Method breakdown (Gurmukhi entries):
- exact_nohyphen (gurmukhi_stem + "Shahmukhi.php"): 56
- exact_hyphen (gurmukhi_stem + "-Shahmukhi.php"): 10
- normalized (hyphens stripped, lowercased, then compared): 145
- unmatched: 617

### Normalized-match audit (output/match_audit.csv)

145 of 211 pairs (69%) were matched via the hyphen-stripped normalization
rule, meaning most of the matched dataset depends on that rule being
correct. Every normalized match was independently re-verified: the
Shahmukhi stem's normalized form, with the trailing "shahmukhi" suffix
removed, must be character-identical to the Gurmukhi stem's normalized
form. Any pair failing that check would be marked suspicious=True.

0 suspicious normalized matches found (0 = every normalized match differs from its pair by hyphenation only, independently re-verified).

## Headline counts

- Total Gurmukhi poet entries: 828
- Total Shahmukhi poet entries: 227
- Gurmukhi : Shahmukhi ratio: 3.65 : 1
- Matched pairs (appear in both scripts, by filename convention): 211
- Gurmukhi poets with a Shahmukhi counterpart: 211 / 828 (25.5%)
- Shahmukhi poets with a Gurmukhi counterpart: 211 / 227 (93.0%)
- Unmatched Gurmukhi-only entries: 617
- Unmatched Shahmukhi-only entries: 16

### The headline asymmetry

The central result of this dataset is the asymmetry between the two
percentages above: only 25.5% of Gurmukhi poets have a
Shahmukhi counterpart, while 93.0% of Shahmukhi poets have a
Gurmukhi counterpart. In other words, the Shahmukhi collection on this site
is small and almost entirely a subset of the Gurmukhi collection, while the
reverse is far from true.

**These figures describe the composition of one website and should not be
generalized to Punjabi publishing, readership, or literary circulation
overall. The asymmetry indicates that this site's Shahmukhi collection
largely overlaps with its Gurmukhi collection; it does not by itself
establish how the Shahmukhi pages were produced.**

### The 16 Shahmukhi-only poets

Small enough to list in full -- each is either a genuine Shahmukhi-only
poet or a filename edge case the three matching methods didn't catch.
Not resolved by name-similarity per the matching constraints above; listed
here for manual review.

- Aadha (`AadhaShahmukhi.php`) [inline]
- Ahsan Emre Lahori (`Ahsan-Emre-Lahori-Shahmukhi.php`) [hub]
- Ali Haider Multani (`AliHaiderMultaniShahmukhi.php`) [hub]
- Bihari (`BihariShahmukhi.php`) [inline]
- Chand (`ChandShahmukhi.php`) [inline]
- Gurbhajan Gill (`Gurbhajan-Gill-Shahmukhi.php`) [hub]
- Hazrat Sultan Bahu (`HazratSultanBahuShahmukhi.php`) [hub]
- Matak Rai (`MatakRaiShahmukhi.php`) [inline]
- Maulvi Ghulam Rasool (`MaulaviGhulamRasoolAlampuriShahmukhi.php`) [hub]
- Najaf Jhelumi (`Najaf-Jhelumi-Shahmukhi.php`) [inline]
- Peer Fazal Hussain Gujrati (`Peer-Fazal-Hussain-Gujrati-Shahmukhi.php`) [inline]
- Qamar Hamid Mirza (`Qamar-Hamid-Mirza-Shahmukhi.php`) [inline]
- Sarmad Kashani (`SarmadKashaniShahmukhi.php`) [inline]
- Sayyed Shah Murad (`SayyedShahMuradShahmukhi.php`) [hub]
- Zaheer Kunjahi (`ZaheerKunjahiShahmukhi.php`) [inline]
- Allah YarKhan Jogi (`AllahYarKhanJogiShahmukhi.php`) -- ambiguous index entry [hub]

## Page layout and poem counts

Building poem counts surfaced a site-structure detail not visible from the
index pages alone: poet pages come in two different layouts.
- **hub**: the page links out to separate sub-pages, one per poem or
  collection. poem_count is a meaningful, if approximate, count here (see
  limitations).
- **inline**: the poem(s) are embedded directly as page text, with no
  outbound poem links. poem_count is intentionally left blank for these --
  NOT reported as zero, since the page demonstrably contains poems, they
  are simply not discretely countable via links without reading the script.

Breakdown by script:
- Gurmukhi (828 total): hub=239 (28.9%), inline=589 (71.1%), missing=0
- Shahmukhi (227 total): hub=70 (30.8%), inline=156 (68.7%), missing=1

The hub-layout share is close between the two scripts (28.9% vs
30.8%, a difference of 2.0 percentage
points) -- not large enough to suggest the two sides were built by
noticeably different methods or at different times, at least by this one
signal.

Cross-tab of page_layout against both_scripts (does having a counterpart in
the other script correlate with layout?) is in logs/match_and_analyze.log
(PAGE_LAYOUT_BREAKDOWN / printed cross-tab from the Phase C+D run). On the
Gurmukhi side, hub-layout poets were noticeably more likely to have a
Shahmukhi counterpart than inline-layout poets in this run; see the log for
exact counts, reported without further interpretation.

Total poem links counted on hub-layout pages only:
- Gurmukhi: 1170
- Shahmukhi: 235
(inline-layout pages, roughly 70% of both sides, are excluded from this
sum entirely -- it is not a total poem count for the site.)

## Fetch log summary (logs/fetch.log)

- Log lines: 1062
- Served from cache (no network request): 0
- Freshly fetched (200 OK): 1054
- Errors/non-200 responses: 7

### Confirmed server-side failure: AvtarSinghPashShahmukhi.php

Avtar Singh Pash's Shahmukhi page (`AvtarSinghPashShahmukhi.php`) returned
HTTP 500 on every attempt: 3 attempts during the original Phase B run, then
a further single retry afterward specifically for this page. All 4 attempts
returned the identical 500 response (876 bytes), consistent with a
persistent server-side issue on this specific page rather than a transient
network problem. This entry appears in poet_pairs.csv with
page_layout_shahmukhi=missing and a blank poem_count -- **this represents a
confirmed fetch failure, not an absence of a Shahmukhi page for this
poet.** Avtar Singh Pash's Gurmukhi page fetched normally (hub layout, 10
poem links).

## Further questions

Open questions this dataset raises but does not answer -- left for future
work, not resolved here:

- Whether Shahmukhi pages are transliterations of the corresponding
  Gurmukhi pages, or are drawn from separate printed Shahmukhi sources.
- What the 16 Shahmukhi-only entries represent: genuinely Shahmukhi-only
  poets, or filename edge cases that a stricter or different matching rule
  would have paired.
- Whether hub vs. inline page layout correlates with when content was
  added to the site, rather than being purely a poet-by-poet editorial
  choice.

## Limitations

- **Romanized names only.** Names on both index pages are Latin-script
  transliterations, not Gurmukhi or Shahmukhi script. Neither author reads
  either script, so names were scraped verbatim and never transliterated,
  translated, or normalized by hand or by model. Actual script text does
  appear on individual poet pages (confirmed during scraping) but was not
  used for identity matching.
- **Filename-based matching only.** Poets are paired solely by the site's
  filename convention (with a documented hyphenation-normalization
  fallback, independently re-verified above). No fuzzy or name-similarity
  matching was used. A poet present on both sites under a filename none of
  the three methods catches will appear as unmatched on both sides rather
  than paired. Matched pairs are a structural inference from URLs, not a
  verified claim that both pages describe the same person.
- **No biographical data.** This dataset contains no religion, nationality,
  era, or date-of-birth/death fields for any poet. Those require sources
  neither author can independently verify from these pages and were
  explicitly excluded from scope.
- **poem_count is available only for hub-layout pages (~29% of
  the Gurmukhi set, ~31% of the Shahmukhi set).** Inline-layout
  pages (the majority, roughly 70% of both) cannot be counted this way --
  doing so would require reading and segmenting Gurmukhi/Shahmukhi verse
  text, which neither author can do and which this pipeline was
  deliberately built not to guess at. Even for hub pages, poem_count is an
  upper bound: at least one observed page (Baba Sheikh Farid, a Sufi saint
  whose verses appear in the Guru Granth Sahib) included commentary/essay
  links about the poet by other named authors alongside his own works,
  because the site does not structurally distinguish these.
- **Scope excludes Urdu poetry, Hindi poetry, and short-story sections.**
  Both index pages sit on a homepage that also hosts a Urdu Poetry section,
  a Hindi Poetry section, and an external short-story subdomain
  (punjabikahani.punjabi-kavita.com) plus a link to a separate Hindi
  poetry site (hindi-kavita.com). None of these are part of this dataset;
  they were identified and excluded explicitly (see exclusion list above),
  not silently dropped.
- **Counts reflect site structure at time of scrape** (2026-08-06T23:07:13+00:00). The
  site has no version history available to this pipeline; a re-run at a
  later date may produce different counts if the site is edited.
