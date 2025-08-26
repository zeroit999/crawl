import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def get_region_links():
    """Lấy 3 link chính của các vùng miền"""
    main_url = "https://tuyensinhso.vn/diem-chuan.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔄 Đang kết nối đến trang chính...")
        response = requests.get(main_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        region_links = []
        
        # Tìm tất cả các link có chứa từ khóa vùng miền
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            if any(keyword in href for keyword in ['mien-bac', 'mien-trung', 'mien-nam']):
                full_url = urljoin(main_url, href)
                if full_url not in region_links:
                    region_links.append(full_url)
        
        # Sắp xếp theo thứ tự: Bắc, Trung, Nam
        sorted_links = []
        for region in ['mien-bac', 'mien-trung', 'mien-nam']:
            for link in region_links:
                if region in link:
                    sorted_links.append(link)
                    break
        
        return sorted_links[:3]  # Chỉ lấy 3 link đầu tiên
        
    except Exception as e:
        print(f"❌ Lỗi khi lấy link vùng miền: {e}")
        # Trả về các link mặc định nếu không crawl được
        return [
            "https://tuyensinhso.vn/diem-chuan/diem-chuan-cac-truong-dai-hoc-hoc-vien-khu-vuc-mien-bac-c47979.html",
            "https://tuyensinhso.vn/diem-chuan/diem-chuan-cac-truong-dai-hoc-hoc-vien-khu-vuc-mien-trung-c48009.html",
            "https://tuyensinhso.vn/diem-chuan/diem-chuan-cac-truong-dai-hoc-hoc-vien-khu-vuc-mien-nam-c47986.html"
        ]

def get_university_links(region_url, region_name):
    """Lấy danh sách các link trường đại học từ trang vùng miền"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔄 Đang truy cập {region_name}...")
        response = requests.get(region_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        university_links = []
        
        # Tìm tất cả các link trường đại học - phương pháp tổng quát
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # Lọc các link có chứa 'diem-chuan' và không chứa 'khu-vuc'
            if ('diem-chuan' in href and 
                'khu-vuc' not in href and
                not href.startswith('#')):
                
                full_url = urljoin(region_url, href)
                if full_url not in university_links:
                    university_links.append(full_url)
        
        # Nếu không tìm thấy link nào, thử phương pháp khác
        if not university_links:
            # Tìm theo class hoặc structure thông thường
            for item in soup.find_all(['li', 'div', 'tr']):
                links = item.find_all('a', href=True)
                for a in links:
                    href = a['href']
                    if 'diem-chuan' in href and 'khu-vuc' not in href:
                        full_url = urljoin(region_url, href)
                        if full_url not in university_links:
                            university_links.append(full_url)
        
        return university_links
        
    except Exception as e:
        print(f"❌ Lỗi khi lấy link trường từ {region_name}: {e}")
        return []

def main():
    print("🚀 Bắt đầu crawl dữ liệu từ tuyensinhso.vn")
    print("=" * 70)
    
    # Lấy 3 link vùng miền
    region_links = get_region_links()
    
    if not region_links:
        print("❌ Không tìm thấy link vùng miền")
        return
    
    region_names = {
        'mien-bac': 'Miền Bắc',
        'mien-trung': 'Miền Trung', 
        'mien-nam': 'Miền Nam'
    }
    
    all_university_links = []
    
    # Duyệt qua từng vùng miền
    for region_url in region_links:
        region_key = None
        for key in region_names.keys():
            if key in region_url:
                region_key = key
                break
        
        if region_key:
            region_name = region_names[region_key]
            university_links = get_university_links(region_url, region_name)
            
            print(f"\n📋 {region_name.upper()} - {len(university_links)} trường:")
            print("-" * 70)
            
            for i, link in enumerate(university_links, 1):
                print(f"{i:2d}. {link}")
                all_university_links.append(link)
            
            # Dừng 2 giây giữa các request
            time.sleep(2)
        else:
            print(f"⚠️ Không xác định được vùng miền từ URL: {region_url}")
    
    print("\n" + "=" * 70)
    print(f"✅ Tổng số link trường đại học: {len(all_university_links)}")
    print("=" * 70)

if __name__ == "__main__":
    main()