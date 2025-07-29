import random

class EhliyetContentGenerator:
    def __init__(self):
        self.content = {
            "Araba Sürüş Teknikleri": {
                "Dönüşler": [
                    "Dönüşlerde hızınızı mutlaka azaltın ve sinyal vermeyi unutmayın.",
                    "Sağa dönüşte şerit çizgilerine dikkat edin, aynalarınızı kontrol edin.",
                    "Kavşakta yayalara yol vermeyi unutmayın.",
                    "Virajda direksiyonu yumuşak hareketlerle çevirin.",
                    "Geniş dönüşler yerine kontrollü dar dönüşleri tercih edin."
                ],
                "Yokuş Kalkışı": [
                    "Yokuşta kalkarken el frenini kullanmak güvenlidir.",
                    "Debriyajı yavaş bırakırken gaz verin, kayma riskini azaltın.",
                    "Eğimli yollarda vites seçimine dikkat edin.",
                    "Motoru boğmadan kalkış yapmayı öğrenmek önemlidir.",
                    "Acil durumlarda yokuşta geri kaymamak için araç mesafesini iyi ayarlayın."
                ],
                "Frenleme": [
                    "Frene yavaşça basın, ani fren araç kontrolünü zorlaştırır.",
                    "Kaygan zeminlerde fren mesafesini artırın.",
                    "ABS sistemiyle fren yaparken pedalı bırakmayın.",
                    "Fren balatalarını düzenli kontrol ettirin.",
                    "Dur kalk trafikte frenleri fazla kullanmamaya özen gösterin."
                ]
            },
            "Motosiklet Sürüş Tüyoları": {
                "Kask ve Güvenlik": [
                    "Kask her sürüşte hayat kurtarır.",
                    "Reflektörlü kıyafet gece sürüşlerinde görünürlüğü artırır.",
                    "Dirseklik ve dizlik gibi ekipmanlar koruma sağlar.",
                    "Kaskın çene kayışı mutlaka bağlı olmalı.",
                    "Kaskınızın sertifikalı olduğundan emin olun."
                ],
                "Fren ve Viraj": [
                    "Viraj öncesi yavaşlayın, viraj içinde gaz verin.",
                    "Ani fren arka tekerin kaymasına yol açabilir.",
                    "Motosiklet frenleri ayrı çalışır, ön ve arka dengeyi iyi kurun.",
                    "Virajlarda motosikleti yatırarak denge sağlayın.",
                    "Bozuk zeminlerde fren yaparken dikkatli olun."
                ]
            },
            "Ehliyet Sınavı Tüyoları": {
                "Hazırlık": [
                    "Trafik işaretlerini ezberlemek yerine anlamaya çalış.",
                    "Deneme sınavları çözerek hızını artır.",
                    "Direksiyon sınavı öncesi mutlaka pratik yap.",
                    "Araç bilgilerini çalış, lastik havaları, yağ seviyesi gibi.",
                    "Sınav günü erken git, stresi azalt."
                ],
                "Sınavda": [
                    "Sinyal vermeyi asla unutma, puan kırılır.",
                    "Aynaları düzenli kontrol et.",
                    "Trafik kurallarına harfiyen uy.",
                    "Görevlinin tüm talimatlarını dikkatle dinle.",
                    "Panik yapma, sakin kal."
                ]
            },
            "Trafik Kuralları": {
                "Genel": [
                    "Hız sınırına uymak hayat kurtarır.",
                    "Emniyet kemeri takmadan asla hareket etme.",
                    "Alkollü araç kullanmak yasal değildir ve tehlikelidir.",
                    "Yaya geçitlerinde yayalara yol ver.",
                    "Kırmızı ışıkta geçmek en sık yapılan hatalardandır."
                ],
                "Yaya Güvenliği": [
                    "Okul bölgelerinde yavaşla, çocuklar aniden çıkabilir.",
                    "Gece sürüşünde yayaları fark etmek zordur, dikkatli ol.",
                    "Kaldırımda yürüyen yayalara saygılı ol.",
                    "Yayalara korna çalmak yerine durmak daha doğru bir davranıştır."
                ]
            },
            "Araç Bakımı": {
                "Temel Bakım": [
                    "Motor yağını düzenli değiştirin.",
                    "Lastik hava basınçlarını ayda bir kontrol edin.",
                    "Cam suyu deposunu dolu tutmak görüş için önemlidir.",
                    "Fren hidroliği ve balataları kontrol ettirin.",
                    "Akkü kutup başlarını temiz tutun."
                ],
                "Acil Durum": [
                    "Lastik patlarsa panik yapmadan yavaşlayın ve durun.",
                    "Aracınız hararet yaparsa motoru durdurun ve bekleyin.",
                    "Acil durum üçgenini en az 30 metre geriye koyun.",
                    "Yangın söndürücü ve ilk yardım çantası her araçta olmalı."
                ]
            },
            "Hava Koşullarında Sürüş": {
                "Karlı": [
                    "Kış lastiği olmadan yola çıkmayın.",
                    "Karlı yollarda fren mesafesi 2 kat artar.",
                    "Yavaş sürün, ani hareketlerden kaçının.",
                    "Camlarınızın görüş sağlamasına dikkat edin.",
                    "Kayma durumunda direksiyonu kayma yönüne çevirin."
                ],
                "Yağmurlu": [
                    "Farlarınızı açın, görüş kısıtlanır.",
                    "Islak zeminde hız yapmayın.",
                    "Sileceklerin çalıştığından emin olun.",
                    "Su birikintilerine dikkat edin, aquaplaning riski vardır.",
                    "Fren mesafesi uzar, takip mesafenizi artırın."
                ],
                "Sisli": [
                    "Kısa farları kullanın, uzun far görüşü bozar.",
                    "Sis lambalarınızı yakın.",
                    "Takip mesafenizi ciddi şekilde artırın.",
                    "Yavaş sürün, ani frenlerden kaçının.",
                    "Yol çizgilerini takip ederek ilerleyin."
                ],
                "Rüzgarlı": [
                    "Köprü ve viyadüklerde rüzgar savurabilir, dikkatli olun.",
                    "Büyük araçların yanından geçerken ani rüzgar dalgaları olabilir.",
                    "Direksiyonu sıkıca tutun.",
                    "Motosiklet sürücüleri için tehlike daha fazladır.",
                    "Yana savrulma riskine karşı hazırlıklı olun."
                ]
            "Araba Sürüş Teknikleri": {
                "Dönüşler": [
                    "Dönüşlerde hızınızı mutlaka azaltın ve sinyal vermeyi unutmayın. Ani dönüşler kazalara yol açabilir.",
                    "Sağa dönüş yaparken şerit çizgilerine dikkat edin, yol hakkını kaybetmemek için aynaları kontrol edin.",
                    "Kavşakta dönüş öncesi hızınızı düşürün, yayalara öncelik verin ve el işaretleri kullanın.",
                    "Dönüş sırasında viraj çizgisini takip etmek sürüş güvenliğinizi artırır.",
                    "Geniş dönüşler yapmaktan kaçının, bu hem trafiği aksatır hem de tehlikelidir."
                ],
                "Yokuş Kalkışı": [
                    "Yokuşta kalkış yaparken debriyajı kontrollü bırakın ve ani gaz vermekten kaçının.",
                    "El frenini kullanarak kalkış yapmak daha güvenlidir, aracınız geriye kaymaz.",
                    "Yokuşta durduktan sonra, tekrar hareket için debriyajı yavaş bırakırken gaz verin.",
                    "Yokuş kalkışında motorun boğulmaması için gaz ve debriyajın uyumlu kullanılması gerekir.",
                    "Eğimin çok dik olduğu yollarda vites seçimine dikkat edin."
                ],
                "Frenleme": [
                    "Fren yaparken ayağınızı gazdan çekin ve fren pedalına yavaşça basın.",
                    "Ani fren yapmaktan kaçının, bu araç kontrolünü zorlaştırabilir.",
                    "Kaygan zeminlerde fren mesafesini artırarak dikkatli olun.",
                    "ABS fren sisteminin çalışma prensibini öğrenin, güvenli fren için önemlidir.",
                    "Fren balatalarının düzenli kontrolü güvenliğiniz için şarttır."
                ],
                "Şerit Değiştirme": [
                    "Şerit değiştirirken mutlaka aynaları kontrol edin ve sinyal verin.",
                    "Şerit değiştirirken kör noktaya dikkat edin.",
                    "Yoğun trafikte ani şerit değiştirmemeye özen gösterin.",
                    "Şerit değiştirirken araçların hızını ve mesafesini doğru değerlendirin.",
                    "Uzun yolculuklarda şerit değişimi yapmadan önce planlama yapmak kazaları önler."
                ],
                "Park Etme": [
                    "Park ederken araç etrafını kontrol edin ve yavaş hareket edin.",
                    "Arka park sensörlerini ve kamerayı kullanarak park etmeyi kolaylaştırın.",
                    "Dar alanlarda paralel park pratiği yaparak sınavda başarılı olun.",
                    "Park esnasında sinyal vermeyi unutmayın.",
                    "Eğimli yerlerde park ederken tekerleklerin yönünü doğru ayarlayın."
                ]
            },
            "Motosiklet Sürüş Tüyoları": {
                "Kask ve Güvenlik": [
                    "Kask takmak hayat kurtarır, kesinlikle sürüş sırasında kullanın.",
                    "Koruyucu eldiven ve mont giymek sürüş konforunu artırır.",
                    "Yol koşullarına göre hızınızı ayarlayın ve fren mesafesini koruyun.",
                    "Motosiklet sürerken reflektörlü kıyafetler tercih edin.",
                    "Kaskınızın uluslararası güvenlik standartlarına uygun olduğundan emin olun."
                ],
                "Dönüş ve Fren": [
                    "Dönüşlerde motosikletinizi eğmeyi unutmayın, hızınızı uygun şekilde azaltın.",
                    "Ani fren yapmaktan kaçının, arka teker kayabilir.",
                    "Şerit değiştirmeden önce sinyal verin ve aynalardan kontrol edin.",
                    "Virajlarda yavaşlamak ve doğru pozisyon almak dengeyi sağlar.",
                    "Fren sisteminizi düzenli olarak kontrol edin ve bakımlarını yaptırın."
                ],
                "Bakım": [
                    "Lastik hava basıncını düzenli kontrol edin, bu sürüş güvenliğinizi artırır.",
                    "Fren hidroliği seviyesini periyodik olarak kontrol edin.",
                    "Zincirin yağlanması ve bakımı motosiklet performansını artırır.",
                    "Akü bağlantılarını ve şarj durumunu kontrol edin.",
                    "Fren balatalarını ve disklerini düzenli olarak inceleyin."
                ],
                "Hava Koşullarında Sürüş": [
                    "Yağmur yağarken hızınızı mutlaka azaltın ve fren mesafenizi artırın.",
                    "Islak yollarda ani fren ve ani direksiyon hareketlerinden kaçının.",
                    "Lastiklerin diş derinliğinin yeterli olduğundan emin olun, su birikintilerinde kaymayı önler.",
                    "Sileceklerinizi düzenli kontrol edin, görüş alanınızın net olması hayati önem taşır.",
                    "Farlarınızı mutlaka açın, böylece diğer sürücüler sizi daha iyi görür.",
                    "Sisli havalarda kısa farlarınızı açın, uzun far kullanmak görüşü azaltır.",
                    "Sis lambalarınız varsa kullanın, yolun kenar çizgilerine dikkat edin.",
                    "Hızınızı çok düşük tutun ve takip mesafenizi artırın.",
                    "Sisi delmek için korna kullanmayın, sakin ve dikkatli sürün.",
                    "Sis içinde ani şerit değiştirmeyin, diğer sürücüler sizi fark etmeyebilir.",
                    "Karlı ve buzlu yollarda mümkün olduğunca araç kullanmamaya çalışın.",
                    "Zorunluysa, hızınızı çok düşürün ve yumuşak fren yapın.",
                    "Kış lastiği kullanın, bu lastikler buzlu zeminde daha iyi tutunma sağlar.",
                    "Ani hızlanma ve ani frenlemelerden kaçının, araç kontrolü zorlaşır.",
                    "Araçta kayma başladığında panik yapmayın, direksiyonu kayma yönüne çevirerek kontrolü sağlayın.",
                    "Rüzgarlı havalarda direksiyon hakimiyetinizi güçlendirin, araç aniden savrulabilir.",
                    "Kamyon, otobüs gibi büyük araçların yanından geçerken dikkatli olun, rüzgar dalgalanması olabilir.",
                    "Motosiklet sürücüsüyseniz, özellikle açık alanlarda rüzgara karşı daha temkinli olun.",
                    "Hafif rüzgarlı havalarda bile direksiyonu her iki elinizle tutun.",
                    "Yük taşıyan araçlar rüzgarda daha az kontrol sahibi olabilir, onlara mesafe bırakın.",
                    "Gece sürüşünde farlarınızı ve göstergelerinizi mutlaka kontrol edin.",
                    "Yorgunluk ve dikkat dağınıklığı riskini azaltmak için sık sık mola verin.",
                    "Yayaların ve hayvanların yol kenarlarından çıkabileceğini unutmayın.",
                    "Uzun far kullanımı yaparken karşıdan gelen sürücüyü rahatsız etmeyin.",
                    "Gece görüş mesafesi gündüze göre çok azdır, bu yüzden hızınızı düşürün."
                ]
            },
            "Ehliyet Sınavı İpuçları": {
                "Sınav Hazırlığı": [
                    "Trafik işaretlerini ezberlemek yerine anlamaya çalışın, bu kalıcı öğrenme sağlar.",
                    "Sınav öncesi yeterince dinlenin ve sakin olmaya çalışın.",
                    "Direksiyon hakimiyetini geliştirmek için bol pratik yapın.",
                    "Sınavda dikkat dağıtıcı unsurlardan uzak durun.",
                    "Sınav kurallarını ve süresini önceden öğrenin."
                ],
                "Sınav Sırasında": [
                    "Sinyal vermeyi unutmayın, bu puan kaybettirir.",
                    "Araç kontrolü ve aynalara dikkat edin.",
                    "Park etme ve geri geri gitme sınav bölümlerine hakim olun.",
                    "Direksiyonu her iki elle tutun ve sakin kalın.",
                    "Sınav görevlisinin talimatlarını dikkatle dinleyin."
                ]
            },
            "Trafik Kuralları ve Güvenlik": {
                "Genel Kurallar": [
                    "Hız sınırlarına uymak can güvenliği için çok önemlidir.",
                    "Emniyet kemeri takmadan araç kullanmak yasaktır.",
                    "Alkollü araç kullanmak ağır cezalara neden olur.",
                    "Trafik ışıklarına kesinlikle uyun.",
                    "Yol hakkı kurallarını öğrenin ve uygulayın."
                ],
                "Yaya Güvenliği": [
                    "Yaya geçitlerinde yayalara mutlaka yol verin.",
                    "Okul bölgelerinde hızınızı azaltın ve dikkatli olun.",
                    "Trafik ışıklarına her zaman uyun.",
                    "Yayaların güvenliği için dikkatli olun ve saygı gösterin.",
                    "Gece sürüşlerinde yayaları fark etmek için farlarınızı yakın."
                ]
            },
            "Araç Bakımı": {
                "Periyodik Bakım": [
                    "Motor yağı seviyesini düzenli kontrol edin ve zamanında değiştirin.",
                    "Lastik diş derinliği güvenlik için kritik öneme sahiptir.",
                    "Fren hidroliği seviyesini periyodik olarak kontrol edin.",
                    "Far lambalarının çalıştığını düzenli kontrol edin.",
                    "Cam suyu deposunu dolu tutun."
                ],
                "Acil Durum Bakımı": [
                    "Lastik patladığında sakin olun, direksiyonu sıkıca tutun ve yavaşça durun.",
                    "Araçta bir arıza durumunda çekici çağırmak en güvenli seçenektir.",
                    "Araçta yangın çıkarsa, uygun yangın tüpü ile müdahale edin.",
                    "Akü boşaldığında takviye kablosu kullanmayı öğrenin.",
                    "Frenlerde anormal ses veya tepki varsa servise gidin."
                ]
            }
        }

      def generate_tip(self):
        category = random.choice(list(self.content.keys()))
        subtopic = random.choice(list(self.content[category].keys()))
        tip = random.choice(self.content[category][subtopic])
        return f"{category} - {subtopic}", tip

    def get_weather_condition(self):
        if "Hava Koşullarında Sürüş" in self.content:
            return random.choice(list(self.content["Hava Koşullarında Sürüş"].keys()))
        return "Güneşli"

    def generate_short_tip(self, condition):
        tips = self.content.get("Hava Koşullarında Sürüş", {}).get(condition, ["Güneşli havalarda dikkatli olun."])
        return random.choice(tips)

    def generate_long_tip(self, condition):
        tips = self.content.get("Hava Koşullarında Sürüş", {}).get(condition, [])
        if len(tips) < 2:
            return "Koşul hakkında yeterli bilgi yok."
        t1 = random.choice(tips)
        t2 = random.choice([t for t in tips if t != t1])
        return f"{t1} {t2}"

if __name__ == "__main__":
    gen = EhliyetContentGenerator()
    for _ in range(5_
