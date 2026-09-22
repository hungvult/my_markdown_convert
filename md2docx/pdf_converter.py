"""
Trình chuyển đổi DOCX sang PDF kết hợp cập nhật tự động Mục lục qua LibreOffice UNO API
"""
import os
import sys
import time
import subprocess
from pathlib import Path

def convert_with_uno(docx_path: str, pdf_path: str) -> bool:
    """Sử dụng LibreOffice UNO API để chèn TOC index, tính số trang và xuất PDF"""
    try:
        import uno
        from com.sun.star.beans import PropertyValue
        from com.sun.star.connection import NoConnectException
    except ImportError:
        return False

    docx_file = Path(docx_path).resolve()
    pdf_file = Path(pdf_path).resolve()

    pipe_name = f"lo_pipe_{os.getpid()}_{int(time.time() * 1000) % 100000}"
    cmd = [
        "soffice",
        "--headless",
        "--invisible",
        "--nocrashreport",
        "--nodefault",
        "--nologo",
        "--nofirststartwizard",
        "--norestore",
        f"--accept=pipe,name={pipe_name};urp;StarOffice.ComponentContext"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx
        )

        ctx = None
        for _ in range(60):
            try:
                ctx = resolver.resolve(f"uno:pipe,name={pipe_name};urp;StarOffice.ComponentContext")
                break
            except NoConnectException:
                time.sleep(0.1)

        if not ctx:
            return False

        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

        in_url = uno.systemPathToFileUrl(str(docx_file))
        out_url = uno.systemPathToFileUrl(str(pdf_file))

        p_hidden = PropertyValue("Hidden", 0, True, 0)
        p_readonly = PropertyValue("ReadOnly", 0, False, 0)
        doc = desktop.loadComponentFromURL(in_url, "_blank", 0, (p_hidden, p_readonly))

        if not doc:
            return False

        # 1. Tìm vị trí MỤC LỤC để chèn ContentIndex
        search = doc.createSearchDescriptor()
        search.SearchString = "MỤC LỤC"
        found = doc.findFirst(search)
        if found:
            cursor = doc.getText().createTextCursorByRange(found)
            cursor.gotoRange(found.getEnd(), False)
            doc.getText().insertControlCharacter(cursor, 0, False) # PARAGRAPH_BREAK

            toc = doc.createInstance("com.sun.star.text.ContentIndex")
            toc.setPropertyValue("CreateFromOutline", True)
            toc.setPropertyValue("Title", "")
            doc.getText().insertTextContent(cursor, toc, False)
            toc.update()

        # 2. Cập nhật các trường văn bản
        doc.getTextFields().refresh()

        # 3. Lưu lại bản DOCX đã được cập nhật sẵn bảng Mục lục
        try:
            doc.store()
        except Exception:
            pass

        # 4. Xuất file PDF
        p_filter = PropertyValue("FilterName", 0, "writer_pdf_Export", 0)
        doc.storeToURL(out_url, (p_filter,))
        doc.close(True)
        return True
    except Exception as e:
        print(f"[CẢNH BÁO] UNO conversion gặp lỗi: {e}", file=sys.stderr)
        return False
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

def convert_docx_to_pdf(docx_path: str, pdf_path: str = None) -> bool:
    if not pdf_path:
        pdf_path = str(Path(docx_path).with_suffix(".pdf"))

    print(f"[*] Đang cập nhật Mục lục và chuyển đổi sang PDF: {pdf_path}...")
    success = convert_with_uno(docx_path, pdf_path)
    if success:
        print(f"[THÀNH CÔNG] Đã tạo file PDF đầy đủ Mục lục: {pdf_path}")
        return True

    # Fallback nếu UNO không khả dụng
    if subprocess.call(["which", "libreoffice"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        print("[*] Fallback: Chuyển đổi PDF bằng lệnh LibreOffice chuẩn...")
        target_dir = str(Path(pdf_path).parent)
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", target_dir, docx_path],
            check=True
        )
        return True

    print("[LỖI] Không tìm thấy LibreOffice trên hệ thống.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python3 -m md2docx.pdf_converter <input.docx> [output.pdf]")
        sys.exit(1)

    in_docx = sys.argv[1]
    out_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    ok = convert_docx_to_pdf(in_docx, out_pdf)
    sys.exit(0 if ok else 1)
