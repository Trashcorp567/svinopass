import { useEffect, useState, type MouseEvent, type ReactNode } from "react";
import { createCheckout, fetchTiers, type GenerationMode, type Tier } from "./api/client";
import Hero from "./components/Hero";
import DeliveryInfo from "./components/DeliveryInfo";
import { USE_CASE_LABELS, type UseCaseId } from "./config/useCases";
import SiteHeader from "./components/SiteHeader";
import SiteFooter from "./components/SiteFooter";
import SiteJsonLd from "./components/SiteJsonLd";
import PaymentSuccess from "./pages/PaymentSuccess";
import { usePageMeta } from "./hooks/usePageMeta";
import OfferPage from "./pages/OfferPage";
import PrivacyPage from "./pages/PrivacyPage";
import DeliveryPage from "./pages/DeliveryPage";
import ContactsPage from "./pages/ContactsPage";
import CheckPage from "./pages/CheckPage";
import WatchPage from "./pages/WatchPage";
import WatchSuccessPage from "./pages/WatchSuccessPage";
import NamesPage from "./pages/NamesPage";
import NamesSuccessPage from "./pages/NamesSuccessPage";
import SellPage from "./pages/SellPage";
import SellSuccessPage from "./pages/SellSuccessPage";
import QrPage from "./pages/QrPage";
import QrSuccessPage from "./pages/QrSuccessPage";
import ImageViewPage from "./pages/ImageViewPage";
import ServiceHub from "./components/ServiceHub";
import PageJsonLd from "./components/PageJsonLd";
import PigGameModal from "./components/PigGameModal";

function MainApp() {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [activeUseCase, setActiveUseCase] = useState<UseCaseId | null>(null);
  const [recommendedTierId, setRecommendedTierId] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [generationMode, setGenerationMode] = useState<GenerationMode>("random");
  const [agreed, setAgreed] = useState(false);
  const [payLoading, setPayLoading] = useState(false);
  const [payError, setPayError] = useState<string | null>(null);

  useEffect(() => {
    fetchTiers().then(setTiers).catch(console.error);
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  const handleUseCaseSelect = (useCaseId: UseCaseId, tierId: string) => {
    setActiveUseCase(useCaseId);
    setSelectedTier(tierId);
    setRecommendedTierId(tierId);
  };

  const recommendedFor =
    activeUseCase !== null && recommendedTierId
      ? { tierId: recommendedTierId, label: USE_CASE_LABELS[activeUseCase] }
      : null;

  const handlePay = async () => {
    if (!selectedTier || !email.trim() || !agreed) return;
    setPayLoading(true);
    setPayError(null);
    try {
      const checkout = await createCheckout(selectedTier, email.trim(), generationMode);
      window.location.href = checkout.confirmation_url;
    } catch (e) {
      setPayError(e instanceof Error ? e.message : "Payment error");
      setPayLoading(false);
    }
  };

  return (
    <>
      <Hero onCta={() => scrollTo("pricing")} />
      <ServiceHub
        tiers={tiers}
        selectedTier={selectedTier}
        activeUseCase={activeUseCase}
        recommendedFor={recommendedFor}
        email={email}
        generationMode={generationMode}
        agreed={agreed}
        payLoading={payLoading}
        onUseCaseSelect={handleUseCaseSelect}
        onTierSelect={setSelectedTier}
        onEmailChange={setEmail}
        onModeChange={setGenerationMode}
        onAgreedChange={setAgreed}
        onPay={() => void handlePay()}
      />
      <DeliveryInfo />
      {payError && <p className="error-banner">{payError}</p>}
    </>
  );
}

const NAV_CONFIRM_MSG = "Пароль ещё генерируется. Уйти на главную?";

function resolvePage(pathname: string, onPasswordWaiting: (waiting: boolean) => void): ReactNode {
  if (pathname.startsWith("/i/")) {
    const token = pathname.slice(3).replace(/\/$/, "");
    return <ImageViewPage token={token} />;
  }

  switch (pathname) {
    case "/payment/success":
      return <PaymentSuccess onWaitingChange={onPasswordWaiting} />;
    case "/offer":
      return <OfferPage />;
    case "/privacy":
      return <PrivacyPage />;
    case "/delivery":
      return <DeliveryPage />;
    case "/contacts":
      return <ContactsPage />;
    case "/check":
      return <CheckPage />;
    case "/watch":
      return <WatchPage />;
    case "/watch/success":
      return <WatchSuccessPage />;
    case "/names":
      return <NamesPage />;
    case "/names/success":
      return <NamesSuccessPage />;
    case "/sell":
      return <SellPage />;
    case "/sell/success":
      return <SellSuccessPage />;
    case "/qr":
      return <QrPage />;
    case "/qr/success":
      return <QrSuccessPage />;
    default:
      return <MainApp />;
  }
}

export default function App() {
  const pathname = window.location.pathname;
  const isSuccessPage = pathname === "/payment/success";
  const [passwordLoading, setPasswordLoading] = useState(isSuccessPage);
  const [pigGameOpen, setPigGameOpen] = useState(false);

  usePageMeta(pathname);

  const handleHomeNav = (event: MouseEvent<HTMLAnchorElement>) => {
    if (isSuccessPage && passwordLoading) {
      event.preventDefault();
      if (window.confirm(NAV_CONFIRM_MSG)) {
        window.location.href = "/";
      }
    }
  };

  return (
    <div className="app">
      {pathname === "/" && <SiteJsonLd />}
      <PageJsonLd pathname={pathname} />
      <SiteHeader onHomeNav={handleHomeNav} onOpenPigGame={() => setPigGameOpen(true)} />
      <main>{resolvePage(pathname, setPasswordLoading)}</main>
      <SiteFooter />
      <PigGameModal open={pigGameOpen} onClose={() => setPigGameOpen(false)} />
    </div>
  );
}
