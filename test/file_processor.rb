# file_processor.rb

class FileProcessor
  def initialize(input_filename, output_filename)
    @input_filename = input_filename
    @output_filename = output_filename
  end

  # 입력 파일에서 내용을 읽고, 각 줄을 대문자로 변환하여 출력 파일에 씁니다.
  def process_file
    unless File.exist?(@input_filename)
      puts "오류: 입력 파일 '#{@input_filename}'을(를) 찾을 수 없습니다."
      return
    end

    lines = []
    begin
      File.open(@input_filename, 'r') do |file|
        puts "파일 '#{@input_filename}'을(를) 읽는 중..."
        file.each_line do |line|
          stripped_line = line.strip # 앞뒤 공백 제거
          capitalized_line = stripped_line.upcase # 대문자로 변환
          lines << capitalized_line
          puts "  원본: '#{stripped_line}' -> 처리: '#{capitalized_line}'"
        end
      end
      puts "파일 읽기 완료."
    rescue IOError => e
      puts "파일 읽기 중 오류 발생: #{e.message}"
      return
    end

    begin
      File.open(@output_filename, 'w') do |file|
        puts "파일 '#{@output_filename}'에 처리된 내용을 쓰는 중..."
        lines.each do |line|
          file.puts line # 파일에 줄 쓰기
        end
      end
      puts "파일 쓰기 완료."
      puts "성공적으로 처리되었습니다. 결과는 '#{@output_filename}'에서 확인할 수 있습니다."
    rescue IOError => e
      puts "파일 쓰기 중 오류 발생: #{e.message}"
    end
  end

  # 테스트를 위한 샘플 입력 파일 생성
  def create_sample_input
    sample_content = <<~EOS
      This is the first line.
      hello world.
      Ruby programming is fun!
      Another line with some text.
      end
    EOS
    begin
      File.open(@input_filename, 'w') do |file|
        file.puts sample_content
      end
      puts "샘플 입력 파일 '#{@input_filename}' 생성 완료."
    rescue IOError => e
      puts "샘플 파일 생성 중 오류 발생: #{e.message}"
    end
  end

  # 생성된 파일들을 정리
  def cleanup_files
    [@input_filename, @output_filename].each do |file|
      if File.exist?(file)
        File.delete(file)
        puts "'#{file}' 삭제 완료."
      end
    end
  rescue IOError => e
    puts "파일 정리 중 오류 발생: #{e.message}"
  end
end

if __FILE__ == $PROGRAM_NAME
  input_file = "sample_input.txt"
  output_file = "processed_output.txt"

  processor = FileProcessor.new(input_file, output_file)

  # 샘플 파일 생성
  processor.create_sample_input

  # 파일 처리 시작
  processor.process_file

  # 모든 작업 완료 후 파일 정리 (선택 사항)
  # processor.cleanup_files
end
