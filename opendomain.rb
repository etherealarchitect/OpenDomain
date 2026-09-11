# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://rubydoc.brew.sh/Formula
class Opendomain < Formula
  desc "Open-source domain registrar platform with integrated AI agent CLI"
  homepage "https://github.com/etherealarchitect/OpenDomain"
  url "https://github.com/etherealarchitect/OpenDomain.git",
      tag:      "v0.1.0",
      revision: "4d6bb33f7dcb6a1b8435d1530309262aca2360c0"
  license "MIT"
  head "https://github.com/etherealarchitect/OpenDomain.git", branch: "deploy/public-preview"

  depends_on "python@3.12"

  def install
    ENV["PYTHONPATH"] = libexec
    ENV["PIP_IGNORE_INSTALLED"] = "1"

    # Only install backend/ (the CLI), not frontend/ or infrastructure/
    backend_dir = buildpath/"backend"

    cd "backend" do
      system "python3.12", "-m", "pip", "install", *std_pip_args, "."
    end

    # Add completion scripts
    bash_completion.install "completions/bash/opendomain" => "opendomain"
    zsh_completion.install "completions/zsh/_opendomain"
    fish_completion.install "completions/fish/opendomain.fish"
  end

  def caveats
    <<~EOS
      OpenDomain CLI has been installed!

      Get started:
        opendomain --help

      Connect to your OpenDomain instance:
        opendomain login --api https://app.opendomain.dev/api/v1

      Local development (requires backend running):
        opendomain login --api http://localhost:8000/api/v1

      Need to debug?
        export OPENDOMAIN_DEBUG=1
        opendomain whois example.com
    EOS
  end

  test do
    assert_match "OpenDomain CLI", shell_output("#{bin}/opendomain --help")

    # Test that authentication file is created in proper location
    assert_predicate testpath/".opendomain-auth", :exist?, "Authentication file should be created"

    # Test simple command
    output = shell_output("#{bin}/opendomain version")
    assert_match "opendomain 0.1.0", output
  end
end